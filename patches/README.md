# Stage 2 patch series

These patches apply to a **Chromium source checkout**, not to this repository. They are the
mechanism by which STGR stops being a distribution and becomes a fork.

## Why this is empty

A patch series is only meaningful once there is a runner that can build Chromium. See
[ADR-0002](../docs/decisions/ADR-0002-build-strategy.md) and
[ROADMAP §2](../docs/ROADMAP.md). Committing speculative patches that have never been
compiled is worse than committing nothing: they look authoritative and rot immediately.

## How the series works

`series` is the ordered list, `quilt`-style. Each entry is a file in this directory.

```bash
# apply
cd chromium/src
for p in $(cat ../../patches/series | grep -v '^#'); do
  git apply --3way "../../patches/$p" || exit 1
done

# after editing, regenerate the patch you changed
git diff > ../../patches/0003-default-prefs.patch
```

## Planned patches

| # | File | Target | Effect |
|---|---|---|---|
| 0001 | `0001-branding-strings.patch` | `chrome/app/theme/chromium/BRANDING` | Product name, vendor, copyright compiled in |
| 0002 | `0002-branding-assets.patch` | `chrome/app/theme/chromium/` | Our `.ico` / `.icns` / PNG set replaces Chromium's |
| 0003 | `0003-default-prefs.patch` | `chrome/browser/prefs/browser_prefs.cc` | Privacy and performance defaults baked in for **every** profile, not just new ones |
| 0004 | `0004-disable-telemetry.patch` | `components/metrics/`, upgrade detector | Remove reporting call sites instead of configuring them off |
| 0005 | `0005-custom-toolbar.patch` | `chrome/browser/ui/views/frame/` | Rail toggle, shield button, brand colouring |
| 0006 | `0006-sidebar-rail.patch` | `chrome/browser/ui/views/side_panel/` | Promote the NTP link rail to real chrome |

`0003` is the highest-value patch: it is the difference between "private on new profiles"
and "private on all profiles".

## Rules

1. One logical change per patch. A patch that touches prefs and UI cannot be reviewed.
2. Patches must apply cleanly to the pinned engine tag. Record that tag in
   `config/base.json` under a `source` key when Stage 2 starts.
3. Every patch needs a line in the table above explaining *why*, not just *what*.
4. If a patch changes user-visible behaviour, it needs an ADR.
5. Rebase the series on every engine bump. A stale series is a broken series.
