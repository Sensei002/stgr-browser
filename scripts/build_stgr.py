#!/usr/bin/env python3
"""STGR build orchestrator.

Stages:
  prepare           Copy STGR UI/branding/distribution assets into the Firefox
                    tree (template substitution from stgr-config.json), generate
                    icons, and stage the uBlock Origin XPI.
  build             Configure + compile via ./mach with the STGR mozconfig.
  package           mach package (+ installer), then write SHA256SUMS.txt and
                    build-manifest.json.
  verify-prefs-sync Verify the injected pref blocks in firefox.js exactly match
                    stgr/config/preferences/*.js.
  substitute        Dry-run template substitution (no Firefox tree required).

Commands are run from the repo root. Requires a synced ./firefox checkout for
everything except `substitute`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FIREFOX_DIR, REPO_ROOT, load_config, log, run  # noqa: E402
from lint_prefs_sync import extract_blocks  # noqa: E402

UI_SRC = REPO_ROOT / "stgr" / "ui"
UI_DST = FIREFOX_DIR / "browser" / "components" / "stgr"
BRAND_SRC = REPO_ROOT / "stgr" / "build" / "branding"
BRAND_DST = FIREFOX_DIR / "browser" / "branding" / "stgr"
UBLOCK_SRC = REPO_ROOT / "stgr" / "extensions" / "ublock-origin"

PLACEHOLDERS = {
    "{{SEARCH_URL}}": "https://duckduckgo.com/",
    "{{STGR_VERSION}}": None,
    "{{FIREFOX_VERSION}}": None,
    "{{UPDATE_URL}}": None,
    "{{RELEASE_NOTES_URL}}": None,
    "{{SOURCE_URL}}": None,
    "{{WEBSITE_URL}}": None,
    "{{WEBSITE_DOMAIN}}": None,
}


def _substitutions(cfg: dict) -> dict:
    repo = cfg["product"]["source_repository"]
    version = cfg["product"]["version"]
    rel = cfg["release"]
    return {
        "{{SEARCH_URL}}": "https://duckduckgo.com/",
        "{{STGR_VERSION}}": version,
        "{{FIREFOX_VERSION}}": cfg["firefox"]["upstream_version"],
        "{{UPDATE_URL}}": repo + "/releases",
        "{{RELEASE_NOTES_URL}}": repo + "/releases/tag/"
                                 + rel["tag_prefix"] + version,
        "{{SOURCE_URL}}": repo,
        "{{WEBSITE_URL}}": cfg["product"]["website"],
        "{{WEBSITE_DOMAIN}}": urlparse(cfg["product"]["website"]).netloc,
    }


def substitute_text(text: str, cfg: dict) -> str:
    subs = _substitutions(cfg)
    for key, value in subs.items():
        if value is None:
            raise SystemExit(f"missing substitution for {key}")
        text = text.replace(key, value)
    return text


def cmd_substitute(cfg: dict) -> int:
    for path in [UI_SRC / "newtab" / "newtab.html",
                 UI_SRC / "about" / "aboutStgr.html"]:
        out = substitute_text(path.read_text(encoding="utf-8"), cfg)
        print(f"--- {path.relative_to(REPO_ROOT)} ---")
        print(out)
    return 0


def cmd_prepare(cfg: dict) -> int:
    """Stage STGR assets into the Firefox tree (after patching)."""
    if not FIREFOX_DIR.exists():
        raise SystemExit("no ./firefox checkout. Run: python scripts/update_firefox.py sync")

    # 1. UI resources with template substitution. These land under
    #    browser/components/stgr/res/stgr/… and are packaged by the 0003
    #    moz.build RESOURCE_FILES (dist/bin/res/stgr/… -> root omni.ja ->
    #    resource://gre/res/stgr/…, same mechanism editor/composer uses for
    #    its res/* files). The chrome CSS is shipped inline in
    #    browser-shared.css by patch 0005, not staged here.
    for rel in ["newtab/newtab.html", "newtab/newtab.css", "newtab/newtab.js",
                "about/aboutStgr.html"]:
        src = UI_SRC / rel
        dst = UI_DST / "res" / "stgr" / rel
        if rel.endswith(".html"):
            text = substitute_text(src.read_text(encoding="utf-8"), cfg)
        else:
            text = src.read_text(encoding="utf-8")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        log("prepare", f"staged res/stgr/{rel}")

    # 1b. Branding logo — the new-tab and about pages reference it relative
    #     (../branding/stgr-logo.svg), so it must exist inside the staged
    #     stgr resource tree and be listed in the 0003 moz.build
    #     RESOURCE_FILES (packaged at resource://gre/res/stgr/branding/).
    logo_src = REPO_ROOT / "stgr" / "branding" / "stgr-logo.svg"
    if logo_src.exists():
        logo_dst = UI_DST / "res" / "stgr" / "branding" / "stgr-logo.svg"
        logo_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(logo_src, logo_dst)
        log("prepare", "staged res/stgr/branding/stgr-logo.svg")

    # 2. Branding directory. Firefox's mozbuild sandbox requires the
    #    --with-branding directory to be inside topsrcdir, so keep the
    #    repository copy as the source of truth and stage a clean build copy
    #    into browser/branding/stgr before mach configures the tree.
    BRAND_DST.mkdir(parents=True, exist_ok=True)
    for name in ("configure.sh", "moz.build", "branding.nsi",
                 "brand.dtd", "brand.ftl", "brand.properties",
                 "firefox.VisualElementsManifest.xml",
                 "private_browsing.VisualElementsManifest.xml",
                 "VisualElements_150.png", "VisualElements_70.png",
                 "PrivateBrowsing_150.png", "PrivateBrowsing_70.png"):
        shutil.copy2(BRAND_SRC / name, BRAND_DST / name)
    # Branding preferences (installed by FirefoxBranding() via
    # JS_PREFERENCE_FILES -> bin/browser/defaults/preferences/).
    pref_dst = BRAND_DST / "pref"
    pref_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BRAND_SRC / "pref" / "firefox-branding.js",
                 pref_dst / "firefox-branding.js")
    stub_src = BRAND_SRC / "stubinstaller"
    stub_dst = BRAND_DST / "stubinstaller"
    stub_dst.mkdir(parents=True, exist_ok=True)
    for name in ("installing_page.css", "profile_cleanup_page.css"):
        shutil.copy2(stub_src / name, stub_dst / name)
    # Locale build support: `mach package` builds the en-US langpack, which
    # requires browser/branding/stgr/locales/Makefile (generated from the
    # locales/moz.build declared via DIRS in moz.build). Stage the same files
    # upstream branding dirs ship (moz.build + jar.mn + en-US brand strings).
    loc_src = BRAND_SRC / "locales"
    loc_dst = BRAND_DST / "locales"
    loc_dst.mkdir(parents=True, exist_ok=True)
    for name in ("moz.build", "jar.mn"):
        shutil.copy2(loc_src / name, loc_dst / name)
    enus_dst = loc_dst / "en-US"
    enus_dst.mkdir(parents=True, exist_ok=True)
    for name in ("brand.ftl", "brand.properties"):
        shutil.copy2(loc_src / "en-US" / name, enus_dst / name)

    # Icons are generated from the master logo. Copy unconditionally so a
    # regenerated set always replaces stale files in the in-tree branding dir.
    icon_dir = REPO_ROOT / "stgr" / "branding" / "icons"
    if not (icon_dir / "stgr.ico").exists():
        log("prepare", "no icons yet — running make_icons")
        run([sys.executable, "scripts/make_icons.py"])
    shutil.copy2(icon_dir / "stgr.ico", BRAND_DST / "firefox.ico")
    for size in (16, 32, 48, 64, 128, 256, 512):
        png = icon_dir / f"icon-{size}.png"
        target = BRAND_DST / f"default{size}.png"
        if png.exists():
            shutil.copy2(png, target)
        else:
            target.unlink(missing_ok=True)
    run([sys.executable, "scripts/make_installer_assets.py",
         "--output", str(BRAND_DST), "--icon", str(icon_dir / "stgr.ico")])
    log("prepare", "branding staged in firefox/browser/branding/stgr")

    # 3. uBlock Origin XPI (official signed build) into distribution/.
    xpi = UBLOCK_SRC / f"uBlock0_{cfg['ublock']['version']}.firefox.signed.xpi"
    dist = FIREFOX_DIR / "distribution"
    if xpi.exists():
        dist.mkdir(exist_ok=True)
        ext_dir = dist / "extensions"
        ext_dir.mkdir(exist_ok=True)
        shutil.copy2(xpi, ext_dir / (cfg["ublock"]["extension_id"] + ".xpi"))
        policies = {
            "policies": {
                "ExtensionSettings": {
                    cfg["ublock"]["extension_id"]: {
                        "installation_mode": "force_installed",
                        "install_url": "file:///distribution/extensions/"
                                       + cfg["ublock"]["extension_id"] + ".xpi",
                    }
                }
            }
        }
        (dist / "policies.json").write_text(
            json.dumps(policies, indent=2) + "\n", encoding="utf-8")
        log("prepare", "uBlock Origin staged via distribution/")
    else:
        log("prepare", f"WARNING: uBlock XPI missing ({xpi.name}). "
                       "Run: python scripts/fetch_ublock.py")
    return 0


def _canonical_block(path: Path) -> str | None:
    """Extract the canonical BEGIN…END pref block from a canonical pref file.

    Reuses lint_prefs_sync.extract_blocks so both verifiers share one
    implementation (no drift risk). Normalizes CRLF so the check works on
    Windows checkouts where git may have written firefox.js with CRLF.
    Returns None if the file is missing a BEGIN or END marker.
    """
    blocks = extract_blocks(path.read_text(encoding="utf-8"))
    if len(blocks) != 1:
        return None
    return "\n".join(next(iter(blocks.values()))).strip()


def cmd_verify_prefs_sync(cfg: dict) -> int:
    """Assert injected pref blocks in firefox.js match the canonical files."""
    firefox_js = FIREFOX_DIR / "browser" / "app" / "profile" / "firefox.js"
    if not firefox_js.exists():
        raise SystemExit("firefox.js not found — sync + patch first")
    source = firefox_js.read_text(encoding="utf-8").replace("\r\n", "\n")
    failures = []
    for canonical in ["stgr.js", "privacy.js", "performance.js"]:
        path = REPO_ROOT / "stgr" / "config" / "preferences" / canonical
        block = _canonical_block(path)
        if block is None:
            failures.append(canonical + " (missing BEGIN/END markers)")
        elif block not in source:
            failures.append(canonical)
    if failures:
        print("PREF SYNC FAILED for: " + ", ".join(failures))
        return 1
    print("pref sync OK (stgr.js, privacy.js, performance.js)")
    return 0


def _source_info(cfg: dict) -> dict | None:
    """Resolve the source-repo env vars Firefox's packaging requires.

    Firefox reads MOZ_SOURCE_REPO / MOZ_SOURCE_CHANGESET from the environment
    at configure time (toolkit/moz.configure) and stores them in
    buildconfig.substs; `mach package` then runs informulate.py (gated on
    MOZ_AUTOMATION), which hard-fails with KeyError when they are absent.
    informulate.py also reads MOZ_BUILD_DATE from the environment (formatted
    %Y%m%d%H%M%S). Mozilla's own automation injects all three. Our checkout
    is a git clone of the pinned upstream release tag, so report that
    repository and the checked-out commit, and stamp MOZ_BUILD_DATE from the
    clock. Returns None when the checkout cannot be resolved (callers then
    fall back to whatever the environment already provides).
    """
    repo = cfg["firefox"]["upstream_repository"]
    try:
        head = run(["git", "rev-parse", "HEAD"], cwd=FIREFOX_DIR,
                   check=True, capture=True).stdout.strip()
    except Exception:
        return None
    if not head:
        return None
    return {
        "MOZ_SOURCE_REPO": repo,
        "MOZ_SOURCE_CHANGESET": head,
        "MOZ_BUILD_DATE": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        # informulate.py (run by `mach package` under MOZ_AUTOMATION) reads
        # MH_BRANCH from the environment and dies with KeyError when it is
        # missing; Mozilla's own CI sets it to the source tree name.
        "MH_BRANCH": f"stgr-{cfg['firefox']['upstream_branch']}",
    }


def mach(cfg: dict, *args: str, check: bool = True):
    """Run ./mach inside the Firefox tree with the STGR mozconfig."""
    env = os.environ.copy()
    env["MOZCONFIG"] = str(REPO_ROOT / cfg["build"]["mozconfig"])
    env.setdefault("MOZ_AUTOMATION", "1")
    # Provide the source-repo/build-date metadata the packager expects
    # (Mozilla's automation normally injects these). setdefault so an explicit
    # CI override wins.
    for key, value in (_source_info(cfg) or {}).items():
        env.setdefault(key, value)
    return run([sys.executable, "mach", *args], cwd=FIREFOX_DIR,
               check=check, capture=False, env=env)


def _verify_runtime_modules() -> None:
    """Fail before compiling if startup modules are not part of the tree.

    These modules are imported by browser-init.js at every browser-window
    startup. A missing DIRS entry can therefore produce a successful compile
    and a packaged executable that opens with an unusable blank window.
    """
    required = [
        FIREFOX_DIR / "browser" / "components" / "stgr" / "gamingmode"
        / "STGRGamingMode.sys.mjs",
        FIREFOX_DIR / "browser" / "components" / "stgr" / "updater"
        / "STGRUpdater.sys.mjs",
    ]
    missing = [str(path.relative_to(FIREFOX_DIR)) for path in required
               if not path.is_file()]
    if missing:
        raise SystemExit(
            "runtime modules missing from the patched Firefox tree: "
            + ", ".join(missing)
            + ". Check browser/components/stgr/moz.build DIRS."
        )
    log("build", "runtime ESM modules staged: gamingmode, updater")


def _verify_packaged_contents(dist: Path) -> None:
    """Verify STGR resources landed in the archives used by resource URLs."""
    archives = list(dist.rglob("omni.ja"))
    toolkit = next((path for path in archives
                    if path.parent.name != "browser"), None)
    app = next((path for path in archives
                if path.parent.name == "browser"), None)
    if toolkit is None or app is None:
        raise SystemExit(
            "packaged omni.ja archives not found; cannot verify STGR runtime assets"
        )

    def entries(path: Path) -> set[str]:
        with zipfile.ZipFile(path) as archive:
            return set(archive.namelist())

    toolkit_entries = entries(toolkit)
    app_entries = entries(app)
    missing_toolkit = {
        "res/stgr/about/aboutStgr.html",
        "res/stgr/branding/stgr-logo.svg",
        "res/stgr/newtab/newtab.css",
        "res/stgr/newtab/newtab.html",
        "res/stgr/newtab/newtab.js",
    } - toolkit_entries
    missing_app = {
        "modules/STGRGamingMode.sys.mjs",
        "modules/STGRUpdater.sys.mjs",
    } - app_entries
    if missing_toolkit or missing_app:
        missing = sorted(missing_toolkit | missing_app)
        raise SystemExit(
            "STGR runtime assets missing from the final package: "
            + ", ".join(missing)
            + ". Check RESOURCE_FILES + DIST_SUBDIR in browser/components/stgr/moz.build."
        )
    log("package", "verified STGR resources in toolkit and browser omni.ja")


def cmd_build(cfg: dict) -> int:
    if not (FIREFOX_DIR / "mach").exists():
        raise SystemExit("no mach in ./firefox — sync + bootstrap first")
    from apply_patches import marker_is_valid
    if not marker_is_valid():
        log("build", "tree not patched or marker stale — running apply_patches")
        run([sys.executable, "scripts/apply_patches.py", "apply"])
    cmd_prepare(cfg)
    _verify_runtime_modules()
    cmd_verify_prefs_sync(cfg)
    mach(cfg, "build")
    print("BUILD OK")
    return 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_package(cfg: dict) -> int:
    # On Windows, `mach package` already builds the NSIS installer: packager.mk's
    # make-package target runs `make -C windows installer` (WINNT + ZIP package
    # format), which produces instgen/setup.exe and then `mach repackage
    # installer` to write the final <pkg>.installer.exe into the obj-dir dist.
    # A separate top-level `mach build installer` target is not guaranteed to
    # exist, so do not call it again here.
    mach(cfg, "package")

    # Collect artifacts (mach writes to obj-dir/dist/…). When MOZ_OBJDIR is
    # set (CI moves the obj dir to C: to keep the multi-GB build off the
    # pagefile drive) it takes precedence; otherwise use mach's default
    # obj-*/dist inside the Firefox tree.
    obj_dir = os.environ.get("MOZ_OBJDIR")
    if obj_dir:
        dist = Path(obj_dir) / "dist"
        if not dist.is_dir():
            raise SystemExit(f"MOZ_OBJDIR dist missing: {dist}")
    else:
        dist = next(FIREFOX_DIR.glob("obj-*/dist"), None)
        if dist is None:
            raise SystemExit("no obj-*/dist found after package")
    _verify_packaged_contents(dist)
    version = cfg["product"]["version"]
    releases = REPO_ROOT / "releases"
    releases.mkdir(exist_ok=True)
    prefix = f"STGR-Browser-{version}-Win64"

    installer_candidates = (list(dist.glob("*.exe"))
                            + list(dist.glob("installer/*.exe"))
                            + list(dist.glob("install/sea/*.exe"))
                            + list(dist.glob("install/**/*.exe")))
    # The full NSIS installer is named <pkg-basename>.installer.exe (e.g.
    # firefox-153.0.en-US.win64.installer.exe); match by suffix/substring
    # rather than assuming a literal "setup" in the name.
    setup = next((c for c in installer_candidates
                  if "setup" in c.name.lower()
                  or c.name.lower().endswith(".installer.exe")), None)
    if setup is None and len(installer_candidates) == 1:
        setup = installer_candidates[0]
    if setup:
        shutil.copy2(setup, releases / f"{prefix}-Setup.exe")
        log("package", f"installer -> releases/{prefix}-Setup.exe")
    elif cfg["build"].get("installer"):
        log("package", "WARNING: no installer .exe found in obj dist — "
                        "the release will lack a Setup.exe")

    if cfg["build"].get("portable_archive"):
        app_dir = dist / "firefox"
        if not app_dir.is_dir():
            app_dir = dist / "bin"
        if app_dir.is_dir():
            zip_path = releases / f"{prefix}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in sorted(app_dir.rglob("*")):
                    if f.is_file():
                        zf.write(f, f.relative_to(app_dir))
            log("package", f"portable -> releases/{prefix}.zip")
        else:
            log("package", "WARNING: packaged app dir not found — "
                            "portable archive skipped")

    from generate_checksums import write_checksums
    write_checksums(releases, releases / cfg["release"]["checksums"])
    write_manifest(cfg, releases / "build-manifest.json")
    print(f"PACKAGE OK — artifacts in {releases}")
    return 0


def write_manifest(cfg: dict, out: Path) -> None:
    """Generate build-manifest.json from the template + config + git state."""
    template = (REPO_ROOT / "stgr" / "build" / "build-manifest.template.json")
    data = json.loads(template.read_text(encoding="utf-8"))
    data["stgr_version"] = cfg["product"]["version"]
    data["firefox_version"] = cfg["firefox"]["upstream_version"]
    data["platform"] = cfg["build"]["target"]
    state_file = REPO_ROOT / ".stgr" / "state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        data["firefox_revision"] = state.get("FIREFOX_REVISION", "")
    data["source_date"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data["patches"] = [
        line.strip() for line in
        (REPO_ROOT / "patches" / "series").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    log("package", f"manifest -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description="STGR build orchestrator")
    ap.add_argument("cmd", choices=["prepare", "build", "package",
                                    "verify-prefs-sync", "substitute"])
    args = ap.parse_args()
    cfg = load_config()
    if args.cmd == "prepare":
        return cmd_prepare(cfg)
    if args.cmd == "build":
        return cmd_build(cfg)
    if args.cmd == "package":
        return cmd_package(cfg)
    if args.cmd == "verify-prefs-sync":
        return cmd_verify_prefs_sync(cfg)
    if args.cmd == "substitute":
        return cmd_substitute(cfg)
    return 1


if __name__ == "__main__":
    sys.exit(main())
