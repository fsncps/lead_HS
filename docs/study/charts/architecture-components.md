# System components — leadhs (v0.1.1)

Source of truth: 20_DESIGN/MASTER/architecture.md (module layout) and
docs/study/ARCHITECTURE.md (strategy shape). Rendered with --type component.

## Components

- leadhs CLI (click): db init|status|audit, source load|list, probe run|record, probe report, doctor
- db.py: connect (WAL, foreign_keys=ON), migrate (forward-only + backup), status, audit R1–R9
- store.py: raw store — put/get/verify/orphans; hash-only filenames
- fetch.py: THE fetch seam — robots, rate limit, UA+contact, retry/backoff; injectable clock+sleep
- probe/engine.py: per-source run loop, run lifecycle
- probe/adapters.py: CS / PE / ST adapters + manual recording
- report.py: probe report rendering (md/csv/json)
- doctor.py: environment preflight
- SQLite leadhs.sqlite: probe-era subset (0001–0002) + views
- data/raw/: raw document store (gitignored)

Connections:

- CLI → db.py, store.py, fetch.py, probe/engine.py, report.py, doctor.py
- probe/engine.py → probe/adapters.py, db.py, store.py, fetch.py
- probe/adapters.py → fetch.py (network), store.py (raw archive)
- db.py → SQLite leadhs.sqlite
- store.py → data/raw/

```
┌──────────────────────────────────────────────────────────────┐
│ leadhs CLI (click)  db|source|probe|doctor                    │
└──────┬───────────────────────────────────────────────────────┘
       │ one connection per command (WAL, foreign_keys=ON)
       ▼
┌──────────────┐ ┌──────────────┐ ┌────────────────────────────┐
│ db.py        │ │ fetch.py     │ │ store.py (raw store)       │
│ migrate/audit│ │ robots+rate  │ │ data/raw/<source-id>/      │
└──────┬───────┘ └──────┬───────┘ │   <sha256>.<ext>           │
       │                │         └────────────┬───────────────┘
       ▼                ▼                      ▼
┌──────────────────────────────────────────────────────────────┐
│ probe/engine.py + adapters.py (CS / PE / ST + manual)         │
└──────┬───────────────────────────────────────────────────────┘
       ▼
┌──────────────────────────────────────────────────────────────┐
│ SQLite leadhs.sqlite — probe-era subset (0001–0002) + views   │
└──────────────────────────────────────────────────────────────┘
```
