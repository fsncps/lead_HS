# Session — 2026-10-03 — reconciliation pass (orientation + drift fixes)

unit: (none) / branch: main / stage: concept (3SM v2)
agents: explore subagent (read-only orientation report) + concept
(primary; writes limited to `.3SM/plan/CONCEPT/**`, `.3SM/sessions/**`,
`.3SM/PROJECT.md` by permission rules)

## what happened

- User asked "where are we, everything up to date document-wise?";
  orientation ran as a read-only explore task over git + the planning
  tree (last commit before this session: 383d4ce, 2026-09-19; 14-day
  gap, consistent with the open next-unit decision).
- Verdict: planning docs substantively up to date — unit history,
  decisions, tool state (pyproject 0.2.3, 412 tests, migrations
  0001–0011), and the D40 story reconcile with git exactly;
  frontmatter dates match last-touch commits; nothing uncommitted.
- Five drift findings; user approved fixing all five.

## findings (drift)

1. README.md repository-layout + strategy links still present the
   legacy v1 tree as the live planning tree (pre-migration prose).
2. Legacy `docs/plan/3SM/README.md` self-describes as live/working;
   no read-only banner (the law lives only in AGENTS.md/PROCESS.md).
3. CONCEPT MASTER DECISIONS index overclaimed "D1–D41" while entries
   ran 1–34, 36, 41 — D37–D40 (incl. the BASTA decision) were lookup
   misses; DEV_HISTORY DH2 repeated the imperfect pointer.
4. DESIGN MASTER OPEN ITEMS kept a stale bullet (frontmatter normalize
   `unit: v0.1.1` — resolved de facto to `unit: global` by housekeeping
   7f8ebb8); Abstract said "active build unit is v0.1.1".
5. No session record existed for the 2026-09-19 rename session.

## applied (commits)

- 1c62bc1 — CONCEPT MASTER: D37–D40 stub entries + corrected index
  coverage note; DEV_HISTORY DH2 mirror; `updated` bumps.
- 0aaa705 — backfilled S-rec `2026-09-19-migration-2.md`.
- (this record lands in the commit that follows)

## pending (outside this stage's write scope — specs for the applier)

Permission rules deny Concept writes outside `.3SM/plan/CONCEPT/**` +
`.3SM/sessions/**` + `.3SM/PROJECT.md`; apply via build context,
housekeeping (explicit invocation), or direct edit:

- **README.md** (finding 1): repository-layout block — add `.3SM/`
  live planning tree (3SM v2: CONCEPT → DESIGN → ENGINEERING, with
  `plan/` line) above `docs/plan/3SM/`, relabel that block "legacy v1
  planning tree — read-only historical reference" (10_STRATEGY = the
  verbatim unit records; 30_IMPLEMENTATION row already exists in the
  docs table, add it to the layout block); repoint the v0.3 strategy
  links (RAW_SOURCING/MATCHING) from `docs/plan/3SM/10_STRATEGY/` to
  `.3SM/plan/CONCEPT/`; in the detail-docs table, replace the
  `10_STRATEGY/MASTER.md` row with the live
  `.3SM/plan/CONCEPT/MASTER.md` (decision register) and mark the
  `20_DESIGN/` + `3SM README` rows historical; mark the "reviewed
  technical design" pointer (tool section) historical with live
  `.3SM/plan/DESIGN/` beside it. Per D23: leave README.de/fr
  `source_updated` behind as drift markers (recommended) or update in
  the same change set.
- **docs/plan/3SM/README.md** (finding 2): prepend a read-only banner
  ("read-only since 2026-09-18; live tree `.3SM/`; unit history
  `.3SM/plan/CONCEPT/DEV_HISTORY.md`") and reword the "working
  documents / design stage holds v0.1.1" sentence to past tense.
  Sanctioned single edit to the otherwise read-only tree.
- **.3SM/plan/DESIGN/MASTER.md** (finding 4): OPEN ITEMS bullet 1 →
  CLOSED 2026-09-18 (housekeeping 7f8ebb8; frontmatter uniformly
  `unit: global`); Abstract sentence → past tense ("Units v0.1.1 …
  v0.2.4 were designed and built under this stage; none is active").
  Belongs to the design stage / design-master pass.

## next

- No lifecycle transitions performed; nothing staged. Next-unit
  decisions remain OPEN (plan/MASTER OPEN ITEMS): unit id + theme,
  MATCHING / RAW_SOURCING / INPUT-MSE adoption verdicts, legacy-tree
  disposition, AGENTS.md thin-pointer conversion.
