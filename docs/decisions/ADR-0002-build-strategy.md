# ADR-0002 — Distribution build, not a source fork (for now)

**Status:** accepted, with a planned successor (Stage 2)
**Date:** 2026-11-01

## Context

The brief: a Chromium-based browser, Helium-like performance, no telemetry, extension
support, lowest possible RAM, **built entirely on GitHub CI/CD, no compilation on a local
machine**.

There are two ways to produce a Chromium-based browser:

1. **Fork Chromium.** `depot_tools`, `gclient sync`, 20–100 GB of source, a full toolchain,
   then 4–8 hours of compilation per architecture. Total control over every string, every
   default, every pixel of chrome.
2. **Distribute Chromium.** Take a prebuilt binary, rebrand it, inject defaults, package it.

The constraint "entirely on GitHub CI/CD" is the deciding factor, and it is worth stating the
limit plainly because it is not widely understood:

> **A Chromium source build cannot run on a GitHub-hosted runner.** The build needs roughly
> 100 GB of working disk and 32+ cores. `windows-latest` provides 14 GB of free disk and 4
> cores. This is not a tuning problem; it is off by an order of magnitude on both axes.
> Larger hosted runners exist on paid plans but still do not reach the disk requirement
> comfortably.

So the real choice was: (a) a distribution build that genuinely runs on hosted CI today, or
(b) a source build that requires a self-hosted runner and therefore does not satisfy the
constraint as written.

## Decision

Ship a **distribution build** as Stage 1. Structure the repository so a source build can be
added as Stage 2 without rework:

- `patches/` holds a `series` file and a README describing the patch order.
- `.github/workflows/build-from-source.yml` is scaffolded for a self-hosted runner labelled
  `chromium-builder`, `workflow_dispatch` only.
- The build orchestrator treats the engine as an opaque, pinned input (`config/base.json`),
  so swapping "download a binary" for "build from source" is a change to one function.

The base is a pinned Chromium continuous build from the official snapshot bucket. It is
pinned by revision and, once `base.lock.json` is committed, by sha256.

## Reasoning

**Why not just wait for a self-hosted runner?** Because a browser that does not exist cannot
be evaluated. Stage 1 produces something installable this week, which is what makes the
product decisions in Stage 2 informed rather than speculative.

**Why the official snapshot bucket and not a third-party Chromium build?** Provenance. The
bucket is Google-operated, the revision number is verifiable, and the archive hash is
pinnable. A community build would put an unauditable binary in the trust path of every user.

**What we give up.** Product strings inside the binary still say "Chromium" in a few
surfaces (about box, some error pages). The tab strip and toolbar are upstream Views UI —
recolourable, not restructurable. Defaults reach new profiles only, because
`initial_preferences` is a first-run hook. These are precisely the items in
[ROADMAP.md](../ROADMAP.md) Stage 2.

**What we do not give up.** Telemetry control (three layers, including policy which reaches
existing profiles), ad blocking, the New Tab Page, the installer, the icon set, the version
resources, and the launch flags. That is most of what a user actually perceives.

## Consequences

- A user-visible "Chromium" string can appear in a few places until Stage 2 lands. Documented,
  not hidden.
- Engine updates are a `config/base.json` bump, not a rebase. This is a genuine advantage:
  upstream security fixes arrive in days, not weeks.
- Stage 2 is a real project with a real hardware prerequisite, not a weekend task. Anyone
  planning it should read [ROADMAP.md](../ROADMAP.md) §2.1 first.
- If a self-hosted runner never materialises, Stage 1 remains a legitimate, shippable
  product. That is the point of the split.
