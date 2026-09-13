---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# Unit v0.2.1 — Implementation plan: source-level capability sounding-out

> **Drafted 2026-09-14.** Executable phase plan for the D33
> source-level expansion (strategy `../../10_STRATEGY/v0.2.1.md`,
> DRAFT; design `../../20_DESIGN/units/v0.2.1.md`, cap1–cap7 + CEO/
> ENG reviews 2026-09-14). Six self-contained PHASE files in the
> house format (objective, preconditions, governing references,
> steps, deliverables, exit gate). **The ENG review ran 2026-09-14
> (mode HOLD SCOPE): findings A1–A2, C1–C3 folded into the design
> doc and the PHASE files; cap5 resolved to a new `ASAdapter`; the
> capability csv widens the existing per-source matrix rows.** This
> unit rides the v0.2.0 machinery (recon precedent nu1, od8 report
> layer, probe engine write-path, metrics sync test) — no new CLI
> command (V9), no new pipeline stage. PHASE03/PHASE04 touch the
> real network (official exports/APIs, manual-web, robots-compliant
> recon — no scraping, D31) and require the explicit `GO=1`.

## Abstract

The executable phase plan for unit v0.2.1 (the D33 source-level
sounding-out). v0.2.0 counted *what a source exposes* (sitemap
product URLs, SDS-library visible). v0.2.1 must answer, per source:
**is an entry actually a real product per the study's model —
(CN8 code, manufacturer, manufacturer product-ident) — and at what
volume and depth?** The unit expands the source register (ecolabel/
EPD registers, PRODCOM and national statistics, CEPE/national
associations, enumerated PE universe) and characterizes each source
against the model — capability profile, volume, data depth, CN8
linkage — then assembles a preliminary N2 numerator. Reconnaissance
only (D31): no product DB seeding, no scraping.

## Scope

Capability profile (six new probe_metrics + probe_mode `capability`)
+ register-capability branch under a new `ASAdapter` (CSV/API
automated; XLSX/auth-gated + PE universe manual-record) + register
expansion (AS/CS/ST/PE rows) + report extension (capability matrix +
preliminary N2 numerator). No new CLI commands (one probe_mode value,
one make target pair); no new pipeline stages; product data only
(D27). CN8 codes and the PRODCOM↔CN8 / EuPCS↔CN8 mapping tables defer
to 0008/M1 (cap6).

## Phase tracking

| # | Focus | Depends on | Exit gate (summary) | Status |
|---|---|---|---|---|
| 01 | Migration 0007: capability mode + 6 capability metrics + metrics.py seeds + sync test | — | 0007 applies; sync 0001+0003+0004+0005+0006+0007 green | done |
| 02 | Code delta: ASAdapter + register-capability branch, `make capability`/MODE var, version 0.2.1, t11 fixture paths | 01 | t11 fixture paths green; audit exit 0; wheel 0.2.1 builds | done |
| 03 | Register expansion (AS/CS/ST/PE rows, EU-only, active flags) + CSV batch | 02 | register loads clean; probe-dry plans every active row | done |
| 04 | Capability execution (official CSV/API exports automated; XLSX/auth-gated/PE-universe manual records; GO=1) | 03 | every capability source recorded or documented-blocked; audit exit 0 | done |
| 05 | Capability report: matrix + N2-numerator render + publish + audit | 03–04 | report per i17/i18 on real data; published; audit exit 0 | done |
| 06 | Docs & close-out (management summary DE/FR, register tables, drift markers, LOG, goldens) | 05 | docs current with the real capability data; translations drift-marked or updated | done |

Statuses: `planned → in-progress → done` (update this table and the
PHASE file header when a phase starts/finishes). Build executes
phases only on explicit user instruction, in order; PHASE03/PHASE04
additionally require the real-network go-ahead (`GO=1`).

## Acceptance criteria

From `../../20_DESIGN/units/v0.2.1.md` (Acceptance criteria) —
verbatim: migration 0007 applies (capability mode + 6 metrics seeded;
sync green through 0007); register-capability branch happy/count/
blocked/malformed per the fixture tests, dry-run plans zero network
calls, `make capability` guarded (GO=1); register loads with the
expanded EU-only source set (AS rows in, auth-gated/XLSX active=0,
PE-universe rows enumerated), probe-dry plans every active row;
capability report (md/csv/json) carries matrix + derived predicate +
preliminary N2-numerator line with the certified-subset caveat, every
number provenance-cited, published to `docs/report/`, `db audit` exit
0; full offline suite green incl. t11; goldens regenerated with
review; wheel builds at 0.2.1 (no new commands).

## Open items carried into build

- Register export shapes to confirm during PHASE04 execution: EU
  Ecolabel ECAT CSV column layout; Blue Angel XLSX export; Nordic
  Swan CSV export; per-register paint counts.
- INIES API auth (email + apiKey + read permissions) — confirm
  whether web search suffices for recon, or document-blocked.
- EuPCS↔CN8 proxy decision (PC-PNT-2) and PRODCOM↔CN8 official
  correspondence — deferred to 0008/M1 (cap6); v0.2.1 records the
  linkage mechanism + reachable count only.
- Verify the 13 CN8 codes against the current CN year (EUR-Lex Reg.
  2658/87 as amended) — deferred to 0008/M1.
- PE-universe inclusion caps and per-channel product-ident shapes —
  pin in the PHASE03 CSV batch.

## Handoff note

These files were drafted 2026-09-14 and ENG-reviewed the same day
(mode HOLD SCOPE; findings A1–A2, C1–C3 folded — see the design
doc's ENG review section and the PHASE step texts). Writing these
files implies no freeze, stage advancement, or execution start.
Build executes phases only on explicit instruction, in order;
PHASE03/PHASE04 additionally require the explicit real-network
go-ahead. Commit/push and any stage advancement await explicit user
instruction (3SM process).
