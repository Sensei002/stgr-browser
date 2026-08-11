# Automation

`scripts/update_firefox.py` works in this directory:

```
automation/
├── firefox-153.0/          one directory per upstream sync/update run
│   └── firefox-update-report.md   applied/failed patches, review list
└── *.log                   run logs
```

Rules:

- **No release is published with an unresolved update.** A failed patch in the
  report is release-blocking; fix conflicts, re-verify, then release.
- Rollback is a release-engineering decision: `LAST_KNOWN_GOOD_FIREFOX` /
  `LAST_KNOWN_GOOD_STGR` are recorded in `.stgr/state.json`; never auto-
  downgrade installed users.
- Working directories are gitignored — the *reports* you care about are
  attached to the update PR by `firefox-update.yml`.
