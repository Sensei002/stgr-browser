# ADR-0003 — Ad blocking via compiled declarativeNetRequest rules

**Status:** accepted
**Date:** 2026-11-01

## Context

The browser must block ads and trackers. On Chromium there are three viable mechanisms:

1. **Bundle uBlock Origin (MV2).** The reference implementation. Full ABP filter syntax,
   cosmetic filtering, scriptlets. Chromium is removing MV2 support, and MV2 extensions
   cannot be loaded as unpacked extensions in recent versions in the way they once could.
2. **Bundle uBlock Origin Lite (MV3).** DNR-based, actively maintained, GPL-3.0.
3. **Compile our own DNR ruleset at build time.**

There is also the question of what "no ads" means for a browser whose headline claim is
lowest-possible RAM.

## Decision

Compile hosts-format blocklists into `declarativeNetRequest` static rulesets at build time,
shipped inside `extensions/stgr-shield`. No runtime filter-list download. No content scripts.
No `webRequest`.

## Reasoning

**Memory and CPU are the product.** A content-script blocker runs JavaScript in every frame
of every page to remove nodes and neutralise scripts. That is a measurable per-tab cost, and
it is paid on every navigation. DNR rules are evaluated by the network stack before a socket
opens: the cost is a lookup in a compiled matcher, and a blocked request never exists. For a
browser whose primary claim is "lowest possible RAM", this is not a marginal preference — it
is the only mechanism that does not undercut the headline feature.

**Privacy is structural, not configured.** Because rules ship in the binary, no list server
ever sees the user's IP, and blocking works offline and behind a captive portal. A runtime
download would create exactly the metadata trail the browser claims not to produce.

**Licensing.** uBlock Origin and uBO Lite are GPL-3.0. Bundling GPL code into a distributed
binary creates obligations that conflict with shipping a closed build. Hosts-format lists are
permissive (StevenBlack is MIT), so we compile those instead. `config/blocklists/sources.json`
records the licence of every source and ships the GPL one disabled, with a comment explaining
why.

**Determinism.** The ruleset is an artefact of the repository. Two checkouts at the same
commit produce byte-identical rules, which makes the shield testable in CI.

## Consequences

**We lose, for now:**

- Cosmetic filtering. No element hiding, so a page with a reserved ad slot may show an empty
  box rather than a reflowed layout. This is the most visible gap and the most likely reason
  a user installs uBO Lite alongside.
- Scriptlet injection. Anti-adblock walls that require a scriptlet will not be defeated.
- Per-site granular control. The popup toggles the whole ruleset, not one origin.

**We gain:**

- Zero per-request JavaScript.
- No runtime network dependency.
- A ruleset that can be unit-tested.
- No GPL entanglement.

**Mitigation for the gaps:** extensions are fully supported, so a user who wants cosmetic
filtering can install uBO Lite from the Chrome Web Store. The default experience should be
good, not maximal.

## Revisit when

- Chromium's DNR gains cosmetic filtering (it has not, and the direction of travel is
  against it).
- Or when a permissive-licensed cosmetic filter engine appears that can be compiled rather
  than interpreted.
