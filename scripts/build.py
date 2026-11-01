#!/usr/bin/env python3
"""
STGR Browser - Windows build orchestrator (Stage 1: distribution build).

    python scripts/build.py                     # full build + installer
    python scripts/build.py --skip-fetch        # reuse the cached Chromium base
    python scripts/build.py --no-installer      # staged app dir only (fast QA)
    python scripts/build.py --clean             # wipe build/ and .cache/ first

Pipeline
    1. fetch    download the pinned Chromium base for win-x64, verify sha256
    2. assemble copy -> rename engine -> stamp icon/version -> seed prefs
                -> stage extensions -> compile the flag-bearing launcher
    3. package  run makensis to produce dist/STGR-Browser-Setup-<ver>-x64.exe

Everything is driven by three inputs, never by hardcoded strings:
    branding/brand.json          product identity + colours + assets
    config/flags/flags.conf      runtime switches (balanced / lowmem)
    VERSION  (or $STGR_VERSION)  product version

Why a launcher instead of putting switches on the shortcut: a browser needs the
same flag set for every entry point (shortcut, protocol handler, taskbar jump
list, "open with"). One small WinExe in the app directory owns that, so the
flags can never drift between entry points.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND_PATH = ROOT / "branding" / "brand.json"
BASE_CFG = ROOT / "config" / "base.json"
LOCK = ROOT / "config" / "base.lock.json"
FLAGS = ROOT / "config" / "flags" / "flags.conf"
PREFS = ROOT / "config" / "preferences" / "stgr-defaults.json"
POLICIES = ROOT / "config" / "policies" / "base.json"
VERSION_FILE = ROOT / "VERSION"
NSI_TEMPLATE = ROOT / "overrides" / "windows" / "installer.nsi"

PLATFORM = "windows-x64"
BUILD = ROOT / "build"
CACHE = ROOT / ".cache"
STAGE = BUILD / "app"
DIST = ROOT / "dist"


def log(msg: str) -> None:
    print(f"[build] {msg}", flush=True)


def annotate(msg: str, limit: int = 12) -> None:
    """
    Emit GitHub check-run annotations for a failure.

    CI logs need admin rights to download; annotations do not. Without this, a
    build failure is invisible to anyone (or anything) triaging from the API.
    """
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    lines = [line for line in msg.splitlines() if line.strip()][-limit:]
    for line in lines:
        print("::error::" + line.replace("%", "%25"), flush=True)


def die(msg: str) -> "None":
    print(f"[build] ERROR: {msg}", file=sys.stderr, flush=True)
    annotate(f"build failed: {msg}")
    raise SystemExit(1)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def product_version() -> str:
    env = os.environ.get("STGR_VERSION", "").strip().lstrip("v")
    if env:
        return env
    if VERSION_FILE.exists():
        v = VERSION_FILE.read_text(encoding="utf-8").strip()
        if v:
            return v
    return read_json(BRAND_PATH)["versions"]["initial"]


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    log("$ " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, **kw)


def try_run(cmd: list[str], **kw) -> bool:
    try:
        subprocess.run(cmd, check=True, capture_output=True, **kw)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        log(f"warning: {Path(str(cmd[0])).name} failed -> {exc}")
        return False


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ── flags.conf ───────────────────────────────────────────────────────────────


def parse_flags(profile: str) -> list[str]:
    """Parse [profile:x] / @include blocks, then merge the feature lists."""
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for raw in FLAGS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[profile:") and line.endswith("]"):
            current = line[9:-1].strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)

    resolved: dict[str, str] = {}
    order: list[str] = []

    def expand(name: str, seen: set[str]) -> None:
        if name in seen:
            die(f"circular @include in profile '{name}'")
        if name not in sections:
            die(f"unknown profile '{name}'")
        seen.add(name)
        for entry in sections[name]:
            if entry.startswith("@include "):
                expand(entry.split(None, 1)[1].strip(), seen)
                continue
            key = entry.split("=", 1)[0]
            if key not in resolved:
                order.append(key)
            resolved[key] = entry

    expand(profile, set())
    merged = [resolved[k] for k in order]

    # Chromium honours a single --disable-features/--enable-features per process.
    for switch in ("--disable-features", "--enable-features"):
        values: list[str] = []
        kept: list[str] = []
        for entry in merged:
            if entry.startswith(switch + "="):
                for item in entry.split("=", 1)[1].split(","):
                    item = item.strip()
                    if item and item not in values:
                        values.append(item)
            else:
                kept.append(entry)
        if values:
            kept.append(f"{switch}=" + ",".join(values))
        merged = kept

    return merged


# ── 1. fetch ─────────────────────────────────────────────────────────────────


def resolve_revision(cfg: dict) -> str:
    pinned = str(cfg["revision"])
    if pinned.lower() != "latest":
        return pinned
    bucket = cfg["platforms"][PLATFORM]["bucket"]
    url = f"{cfg['endpoints']['snapshotBase']}/{bucket}/{cfg['endpoints']['lastChangeFile']}"
    log(f"resolving latest revision from bucket {bucket}")
    with urllib.request.urlopen(url, timeout=30) as resp:
        rev = resp.read().decode().strip()
    if not rev.isdigit():
        die(f"unexpected LAST_CHANGE payload: {rev!r}")
    return rev


def fetch_base(update_lock: bool) -> tuple[Path, str]:
    cfg = read_json(BASE_CFG)
    spec = cfg["platforms"][PLATFORM]
    revision = resolve_revision(cfg)

    archive_dir = CACHE / "base"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / f"{revision}-{spec['archive']}"
    url = f"{cfg['endpoints']['snapshotBase']}/{spec['bucket']}/{revision}/{spec['archive']}"

    lock = read_json(LOCK) if LOCK.exists() else {}
    expected = lock.get(PLATFORM, {}).get("sha256")

    if archive.exists() and (expected is None or sha256_of(archive) == expected):
        log(f"base cached: {archive.name}")
    else:
        log(f"downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "STGR-Browser-Build/1.0"})
        with urllib.request.urlopen(req, timeout=900) as resp, open(archive, "wb") as fh:
            shutil.copyfileobj(resp, fh)

    actual = sha256_of(archive)
    if expected and actual != expected:
        die(
            f"sha256 mismatch (expected {expected[:12]}..., got {actual[:12]}...). "
            "Upstream re-published this revision - bump config/base.lock.json on purpose."
        )
    if expected is None:
        log(f"base sha256 {actual}")
        if update_lock:
            lock[PLATFORM] = {"revision": revision, "sha256": actual}
            LOCK.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            log("wrote config/base.lock.json - commit it to pin the base")

    extract = BUILD / "base"
    stamp = extract / ".stamp"
    if stamp.exists() and stamp.read_text(encoding="utf-8") == actual:
        log("base already extracted")
        return extract / spec["root"], revision

    if extract.exists():
        shutil.rmtree(extract)
    extract.mkdir(parents=True, exist_ok=True)
    log("extracting base")
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(extract)
    stamp.write_text(actual, encoding="utf-8")
    return extract / spec["root"], revision


# ── 2. assemble ──────────────────────────────────────────────────────────────


def render_preferences(brand: dict, version: str) -> dict:
    prefs = read_json(PREFS)
    prefs.setdefault("distribution", {}).update(
        {
            "make_chrome_default": False,
            "make_chrome_default_for_user": False,
            "skip_first_run_ui": True,
            "suppress_first_run_bubble": True,
            "do_not_create_desktop_shortcut": True,
            "do_not_create_quick_launch_shortcut": True,
            "do_not_create_taskbar_shortcut": True,
            "do_not_launch_chrome": True,
            "import_bookmarks": False,
            "import_history": False,
            "import_search_engine": False,
            "import_home_page": False,
            "verbose_logging": False,
            "browser": {"name": brand["product"]["name"], "version": version},
        }
    )
    return prefs


def stage_extensions(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    sources = {
        "stgr-ntp": ROOT / "ntp",
        "stgr-shield": ROOT / "extensions" / "stgr-shield",
        "stgr-theme": ROOT / "extensions" / "stgr-theme",
    }
    for name, src in sources.items():
        if not src.exists():
            die(f"extension source missing: {src}")
        target = dest / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)
    log("extensions staged: " + ", ".join(sorted(sources)))


def ensure_rcedit() -> Path | None:
    local = CACHE / "tools" / "rcedit-x64.exe"
    if local.exists():
        return local
    if shutil.which("rcedit"):
        return Path(shutil.which("rcedit"))  # type: ignore[arg-type]
    local.parent.mkdir(parents=True, exist_ok=True)
    url = "https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe"
    try:
        log("downloading rcedit")
        req = urllib.request.Request(url, headers={"User-Agent": "STGR-Browser-Build/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(local, "wb") as fh:
            shutil.copyfileobj(resp, fh)
        return local
    except Exception as exc:  # noqa: BLE001 - branding is best-effort
        log(f"warning: rcedit unavailable ({exc}); engine keeps upstream resources")
        return None


def stamp_engine(exe: Path, brand: dict, version: str) -> None:
    rcedit = ensure_rcedit()
    ico = ROOT / brand["assets"]["iconIco"]
    if not rcedit or not ico.exists():
        log("warning: skipping engine resource stamping")
        return
    ok = try_run(
        [
            str(rcedit), str(exe),
            "--set-icon", str(ico),
            "--set-file-version", version,
            "--set-product-version", version,
            "--set-version-string", "ProductName", brand["product"]["name"],
            "--set-version-string", "FileDescription", brand["product"]["name"],
            "--set-version-string", "CompanyName", brand["product"]["vendor"],
            "--set-version-string", "LegalCopyright", brand["product"]["copyright"],
            "--set-version-string", "InternalName", "stgr",
            "--set-version-string", "OriginalFilename", "stgr.exe",
        ]
    )
    log("engine resources stamped" if ok else "warning: engine resource stamping failed")


def find_csc() -> str | None:
    """
    Locate a C# compiler. Windows runner images have moved this around, so
    check every plausible location instead of assuming the Framework one.
    """
    found = shutil.which("csc") or shutil.which("csc.exe")
    if found:
        return found

    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    for candidate in (
        windir / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe",
        windir / "Microsoft.NET" / "Framework" / "v4.0.30319" / "csc.exe",
    ):
        if candidate.exists():
            return str(candidate)

    # Visual Studio ships Roslyn, which is a perfectly good csc.
    for pattern in (
        r"C:\Program Files\Microsoft Visual Studio\2022\*\MSBuild\Current\Bin\Roslyn\csc.exe",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\*\MSBuild\Current\Bin\Roslyn\csc.exe",
    ):
        for hit in sorted(glob.glob(pattern)):
            if Path(hit).exists():
                return hit
    return None


def compile_launcher(app: Path, flags: list[str], lowmem_delta: list[str], brand: dict) -> Path:
    """
    Small WinExe that owns the flag set for every entry point.

    It also implements two STGR-only switches that never reach the engine:
      --stgr-lowmem   add the low-memory flag delta and start
      --stgr-quit     terminate a running engine (used by the uninstaller)
    """
    cs = app / "launcher.cs"
    literal = " ".join(flags)
    delta = " ".join(lowmem_delta)
    cs.write_text(
        f'''// AUTO-GENERATED by scripts/build.py - do not edit.
using System;
using System.Diagnostics;
using System.IO;
using System.Text;

internal static class StgrLauncher
{{
    private const string Flags = @"{literal}";
    private const string LowMemExtra = @"{delta}";

    [STAThread]
    private static int Main(string[] args)
    {{
        string dir = AppDomain.CurrentDomain.BaseDirectory;
        string engine = Path.Combine(dir, "stgr.exe");
        if (!File.Exists(engine)) engine = Path.Combine(dir, "chrome.exe");

        bool lowmem = false;
        bool quit = false;
        var passthrough = new StringBuilder();
        foreach (string arg in args)
        {{
            if (arg == "--stgr-lowmem") {{ lowmem = true; continue; }}
            if (arg == "--stgr-quit") {{ quit = true; continue; }}
            passthrough.Append(" \\"").Append(arg.Replace("\\"", "\\\\\\"")).Append("\\"");
        }}

        if (quit)
        {{
            foreach (var p in Process.GetProcessesByName("stgr"))
            {{
                try {{ p.CloseMainWindow(); p.WaitForExit(1500); p.Kill(); }}
                catch (Exception) {{ }}
            }}
            return 0;
        }}

        string profile = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "{brand['product']['shortName']}", "Browser");
        Directory.CreateDirectory(profile);

        var sb = new StringBuilder();
        sb.Append(Flags);
        if (lowmem) sb.Append(" ").Append(LowMemExtra);
        sb.Append(" --user-data-dir=\\"").Append(profile).Append("\\"");
        sb.Append(" --load-extension=\\"");
        sb.Append(Path.Combine(dir, "extensions", "stgr-ntp")).Append(",");
        sb.Append(Path.Combine(dir, "extensions", "stgr-shield")).Append(",");
        sb.Append(Path.Combine(dir, "extensions", "stgr-theme")).Append("\\"");
        sb.Append(passthrough.ToString());

        Process.Start(new ProcessStartInfo(engine, sb.ToString())
        {{
            UseShellExecute = false,
            WorkingDirectory = dir
        }});
        return 0;
    }}
}}
''',
        encoding="utf-8",
    )

    out = app / "STGRBrowser.exe"
    csc = find_csc()
    if not csc:
        die("csc.exe not found - cannot build the launcher (needs .NET Framework 4.x or Roslyn)")
    log(f"compiling launcher with {csc}")
    run([csc, "/nologo", "/target:winexe", f"/out:{out}", str(cs)])
    if not out.exists():
        die(f"csc reported success but produced no {out.name}")
    cs.unlink(missing_ok=True)
    log(f"launcher compiled: {out.name} ({out.stat().st_size // 1024} KiB)")
    return out


def assemble(brand: dict, version: str, revision: str, skip_fetch: bool) -> Path:
    if skip_fetch:
        base = BUILD / "base" / read_json(BASE_CFG)["platforms"][PLATFORM]["root"]
        if not base.exists():
            die("--skip-fetch given but build/base is empty")
        log("reusing existing base")
    else:
        base, revision = fetch_base(update_lock=os.environ.get("STGR_UPDATE_LOCK") == "1")

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.parent.mkdir(parents=True, exist_ok=True)
    log(f"staging app from {base.name}")
    shutil.copytree(base, STAGE)

    engine = STAGE / "chrome.exe"
    if not engine.exists():
        die(f"engine binary missing: {engine}")
    engine.rename(STAGE / "stgr.exe")
    stamp_engine(STAGE / "stgr.exe", brand, version)

    prefs = json.dumps(render_preferences(brand, version), indent=2)
    (STAGE / "initial_preferences").write_text(prefs, encoding="utf-8")
    (STAGE / "master_preferences").write_text(prefs, encoding="utf-8")

    stage_extensions(STAGE / "extensions")

    log("resolving flag profiles")
    balanced = parse_flags("balanced")
    lowmem = parse_flags("lowmem")
    lowmem_delta = [f for f in lowmem if f not in balanced]
    log(f"flags: {len(balanced)} balanced, +{len(lowmem_delta)} for low-RAM mode")
    compile_launcher(STAGE, balanced, lowmem_delta, brand)

    (STAGE / "stgr-build.json").write_text(
        json.dumps(
            {
                "product": brand["product"]["name"],
                "version": version,
                "platform": PLATFORM,
                "engine": "chromium",
                "engineRevision": revision,
                "flags": len(balanced),
                "lowMemFlags": len(lowmem_delta),
                "builtAt": os.environ.get("STGR_BUILD_TIME", ""),
                "commit": os.environ.get("GITHUB_SHA", ""),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return STAGE


# ── 3. package ───────────────────────────────────────────────────────────────


def find_makensis() -> str | None:
    found = shutil.which("makensis") or shutil.which("makensis.exe")
    if found:
        return found
    for candidate in (
        Path(r"C:\Program Files (x86)\NSIS\makensis.exe"),
        Path(r"C:\Program Files\NSIS\makensis.exe"),
        Path(r"C:\ProgramData\chocolatey\bin\makensis.exe"),
    ):
        if candidate.exists():
            return str(candidate)
    return None


def policies_as_registry(policies: dict) -> str:
    """Emit an NSIS WriteRegStr block from the policy JSON."""
    lines = []
    key = r"HKCU\Software\Policies\Chromium"
    for name, value in policies.items():
        if isinstance(value, bool):
            lines.append(f'  WriteRegDWORD HKCU "Software\\Policies\\Chromium" "{name}" {"1" if value else "0"}')
        elif isinstance(value, int):
            lines.append(f'  WriteRegDWORD HKCU "Software\\Policies\\Chromium" "{name}" {value}')
        elif isinstance(value, str):
            lines.append(f'  WriteRegStr HKCU "Software\\Policies\\Chromium" "{name}" "{value}"')
        else:
            log(f"warning: policy {name} has unsupported type, skipped")
    log(f"policies emitted for {key}: {len(lines)}")
    return "\n".join(lines)


def vi_version(version: str) -> str:
    """NSIS VIProductVersion needs exactly four numeric parts."""
    parts = re.findall(r"\d+", version)[:4]
    while len(parts) < 4:
        parts.append("0")
    return ".".join(parts)


def package(brand: dict, version: str) -> Path | None:
    makensis = find_makensis()
    if not makensis:
        # Failing loudly beats producing an empty dist/ that only breaks three
        # steps later with "no such file: *.exe".
        die("makensis not found - install NSIS or add it to PATH before packaging")

    DIST.mkdir(parents=True, exist_ok=True)
    outfile = DIST / f"STGR-Browser-Setup-{version}-x64.exe"
    outfile.unlink(missing_ok=True)

    reg_block = policies_as_registry(read_json(POLICIES))
    reg_script = BUILD / "policies.nsh"
    reg_script.write_text(reg_block + "\n", encoding="utf-8")

    defines = [
        f"/DVERSION={version}",
        f"/DVI_VERSION={vi_version(version)}",
        f"/DPRODUCT_NAME={brand['product']['name']}",
        f"/DPRODUCT_SHORT={brand['product']['shortName']}",
        f"/DPUBLISHER={brand['product']['vendor']}",
        f"/DPRODUCT_URL={brand['product']['homepage']}",
        f"/DAPP_ID={brand['product']['appIdWindows']}",
        f"/DPROTOCOL={brand['product']['protocol']}",
        f"/DSRCDIR={STAGE}",
        f"/DOUTFILE={outfile}",
        f"/DICONFILE={ROOT / brand['assets']['iconIco']}",
        f"/DPOLICYSCRIPT={reg_script}",
    ]
    wizard = ROOT / "overrides" / "windows" / "wizard.bmp"
    header = ROOT / "overrides" / "windows" / "header.bmp"
    if wizard.exists():
        defines.append(f"/DWIZARDIMAGE={wizard}")
    if header.exists():
        defines.append(f"/DHEADERIMAGE={header}")

    run([makensis, "/V2", *defines, str(NSI_TEMPLATE)])
    if not outfile.exists():
        die("makensis reported success but produced no installer")
    size_mb = outfile.stat().st_size / (1024 * 1024)
    log(f"installer: {outfile.name} ({size_mb:.1f} MiB)")
    return outfile


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the STGR Browser Windows distribution")
    ap.add_argument("--skip-fetch", action="store_true", help="reuse build/base instead of downloading")
    ap.add_argument("--no-installer", action="store_true", help="stop after staging the app directory")
    ap.add_argument("--clean", action="store_true", help="delete build/ and dist/ first")
    ap.add_argument("--print-flags", metavar="PROFILE", help="dump a resolved flag set and exit")
    args = ap.parse_args()

    if args.print_flags:
        for flag in parse_flags(args.print_flags):
            print(flag)
        return 0

    if args.clean:
        for path in (BUILD, DIST):
            if path.exists():
                shutil.rmtree(path)
        log("cleaned build/ and dist/")

    if os.name != "nt":
        die("this build path targets Windows; run it on a Windows runner")

    brand = read_json(BRAND_PATH)
    version = product_version()
    log(f"{brand['product']['name']} {version} -> {PLATFORM}")

    stage = assemble(brand, version, revision="unknown", skip_fetch=args.skip_fetch)
    log(f"staged {sum(1 for _ in stage.rglob('*'))} entries in {stage}")

    if args.no_installer:
        log("stopping before packaging (--no-installer)")
        return 0

    installer = package(brand, version)
    if installer is None:
        return 0

    (DIST / "latest.json").write_text(
        json.dumps(
            {
                "product": brand["product"]["name"],
                "version": version,
                "channel": brand["versions"]["channel"],
                "platform": PLATFORM,
                "installer": installer.name,
                "sha256": sha256_of(installer),
                "sizeBytes": installer.stat().st_size,
                "notesUrl": f"{brand['product']['repository']}/releases/tag/v{version}",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001 - top-level crash reporter
        import traceback

        report = traceback.format_exc()
        print(report, file=sys.stderr, flush=True)
        annotate(report)
        raise SystemExit(1)
