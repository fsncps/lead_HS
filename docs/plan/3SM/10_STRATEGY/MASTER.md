---
unit: v0.1.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-12
---

# Strategy MASTER — lead_HS

## Abstract

This is the strategy summary, in plain terms. The project researches
the **EU market** for paints (customs headings 3208/3209, plus a
low-priority annex for artists' colours under 3213): how many products
are on the market, for how many of them detailed documentation
(safety-data-sheet sections) is obtainable, and what that
documentation shows about lead — using only documents collectable for
free from the web. The study is situated in the context of the Swiss
Cassis-de-Dijon exception for lead-containing paints and the related
legislation and decision-making; Switzerland enters as the regulatory
frame only (ban threshold, VIPaV entry), never as a studied market
(D31). The working expectation is that EU regulation has largely
eliminated lead paints; the study tests that against product
documentation. It records the main decisions: what counts as one
"product" (one base formulation), which parts of the market we look at
(all segments; EU-lawful presence is a study object in its own right),
how many products we check (about 2,000–3,000 by statistical
precision, once the frame unit follows), how we detect lead (SDS
Section 3, cross-checked across documents — no laboratory), and the
regulatory frame the evidence feeds into (Swiss ban at 100 ppm total
Pb via ChemRRV Anhang 2.8, shielded from EU-lawful imports by the
VIPaV exceptions catalogue — an autonomous Cassis-de-Dijon exception
whose entire catalogue is reviewed every five years under SECO's
lead). Open questions and the phased roadmap follow.

## DECISIONS

1. **Deliverable:** decision basis for the federal actors around the
   lead-paint exception (regulation owner and review lead; see decision 11
   institutional frame) — briefing on Swiss external trade in 3208/3209
   paints, lead prevalence, and the regulatory seams — plus a reusable
   product/SDS evidence database. **(Amended 2026-09-12 by D31: the
   briefing covers EU-market scale, access coverage and lead
   prevalence; Swiss external trade is no longer part of the
   deliverable.)**
2. **Unit of analysis:** formulation/base product (register-like; colour and
   size variants collapse; point-of-sale tinting variants excluded). Matches
   PCN/SPIN logic and regulatory reality.
3. **Segment scope:** all segments — decorative, industrial/professional
   (anticorrosive, marine, road-marking, coil/OEM) — each additionally split
   by **origin** (Swiss production / EU import / third-country import),
   weighted by Swiss trade statistics. **(Origin split and Swiss-trade
   weighting superseded 2026-09-12 by D31 — metrics are EU-only;
   Switzerland is the regulatory frame, not a studied market.)**
4. **Sampling:** precision-based stratified design (not a literal 10%):
   n ≈ 385/stratum (p=0.5, ±5%), n ≈ 811 (p≈5%, ±1.5%), with FPC where frames
   are small; full design ≈ 2,000–3,000 products. High-risk strata oversampled.
   **(Origin split and Swiss-trade weighting superseded 2026-09-12 by
   D31 — metrics are EU-only; frame unit deferred, D29.)**
5. **Lead detection primary source:** SDS (MSDS) Section 3 parsing against a
   CAS/EC/Index lead-compound dictionary; UFI as join key; Section 15
   authorisation statements as anomaly signal.
6. **CN assignment:** inferred per product from SDS composition (medium +
   binder chemistry → CN8), since products carry no tariff codes.
7. **Corroboration instead of laboratory (supersedes the earlier lab
   validation decision):** no lab, no physical samples. Suspected positives
   are cross-checked against independent documents for the same product
   (TDS, label text, retailer listings, older SDS versions, cross-market
   brand variants). Sub-0.1% and impurity lead remain invisible → stated
   limitation of the study, quantified by assumption, not measurement.
8. **Pilot-first:** Nordic SPIN data provide an immediate, free pilot estimate
   (preparation counts + lead-CAS incidence for DK/SE/NO/FI) before any
   scraping infrastructure is built.
9. **Cost constraint (hard):** publicly retrievable documents only — no paid
   databases, no commercial market reports, no sample purchases.
10. **Swiss workstreams are first-class Phase-0 items:** (a) EZV/swiss-impex
    trade extraction at CN8 × partner; (b) legal dossier EU vs CH (ChemO
    REACH-alignment, third-country import control; MRA deliberately out of
    scope — separate THG instrument, see decision 11). **(Superseded
    2026-09-12 by D31: the EZV extraction is closed and the Swiss
    workstreams dropped — EU-only; legal-text verification stays as
    background documentation.)**
11. **Regulatory anchoring and political protocol (corrected 2026-09-10;
    supersedes the "bilateral" framing):** the study is anchored in the
    **autonomous Swiss Cassis-de-Dijon frame** — THG Art. 16a, one of
    three THG instruments (autonomous harmonization; state-treaty
    agreements/MRA; CdD). It is **not** an EU-bilateral compliance matter;
    MRAs (THG Art. 14) are a separate instrument and out of scope.
    Exceptions (Federal Council; THG Art. 16a Abs. 2 lit. e i.V.m.
    Art. 4 Abs. 3–4: overriding public interests, e.g. health protection)
    were defined at the principle's inception (2010); each protects a
    Swiss technical regulation deviating from EU rules, and each has an
    institutional owner: the requesting federal office, responsible for
    implementation, monitoring and revision. For the lead-paints entry
    (VIPaV Art. 2 Bst. a Ziff. 1, shielding ChemRRV Anhang 2.8's
    ≥0.01% total-Pb ban) the requester/owner is the **BBL** (per
    commissioning context 2026-09-10 — verify against public record before
    naming BBL in deliverables); BAFU enforces; **SECO conducts the
    five-yearly review of the entire exception catalogue** (last 2023:
    keep; next ~2028; criteria Eignung/Erforderlichkeit/
    Verhältnismässigkeit). The study supplies documented EU-market
    numbers within that review cycle — **without presupposing deletion
    or retention outcomes** and without taking a position on the
    regulation itself. Public-facing documents keep the
    commissioning relationship implicit; correct institutional wording
    only. SECO's "Art 2a(1)" read as Art. 2 Bst. a Ziff. 1 (no Art. 2a
    exists; inference, confirm only if load-bearing). Art. 16 VIPaV
    (list keeping; statutory basis THG Art. 31 Abs. 2 — verified via
    Lexaris SR 946.51) is context only.
12. **EU-market leg:** EU-lawful presence of lead paints is a first-class
    study object (the Cassis upstream), not just context. Same SDS method on
    EU-side catalogs. Seed products already documented: Epifanes WERDOL
    Bleimennige (DE marine retail), BRAVA blymönja (SE, professional-only),
    Old Holland Cremnitz White PW1 (NL), Zecchi biacca/giallorino/minio (IT).
13. **HS 3213 census annex:** artists' oil colours with lead pigments
    (lead/Cremnitz white, Naples yellow, lead-tin yellow) are added as a
    small full census (not a sample) — population is tiny (dozens of brands),
    and the stream is invisible in 3208/3209 statistics. Core sampling
    design remains 3208/3209.
14. **Legal-category dimension:** the database classifies each product by
    legal category (Anstrichfarbe/Malfarbe/treated article; Swiss total-Pb
    ban threshold relevance), not only by HS/CN code. **(Superseded by
    D27, 2026-09-11 — the database carries product data only; no legal
    category, no ban-engagement flag.)**
15. **Headline caveat:** the Swiss ban threshold (0.01% = 100 ppm total Pb,
    ChemRRV Anhang 2.8, 2005 wording — current text to verify) lies **below**
    the EU SDS declaration floor (0.1% for classified compounds). A paint
    can be EU-lawful and transparently documented yet exceed the Swiss ban,
    invisibly to the SDS method. Carried as an explicit limitation in every
    deliverable.
16. **Tooling (light data-engineering):** single-user, no-server pipeline
    driven by one CLI (`leadhs`; Python ≥ 3.11, stdlib-first; requests/
    bs4/click/jinja2/pypdf only); state = one SQLite file + hash-addressed
    raw-document store (both gitignored); code, migrations, seed
    dictionaries and final reports in git. No servers/services — fits
    Slackware/no-systemd and the cost constraint. Detail: ARCHITECTURE.md.
17. **Evidence-database principles:** provenance on every record (source
    URL + retrieval date + raw hash); formulation-level products with a
    sighting dedup layer; the declared-vs-total-Pb blind spot encoded as
    a concentration taxonomy (`none_listed` ≠ lead-free); seeded,
    reproducible sampling runs; append-only corrections; unverified
    CAS/EC stay flagged. Schema: DATA_MODEL.md.
18. **Reporting:** every number in generated reports comes from the
    database (cited with run ID + seed); generated technical report DE
    primary, FR secondary, EN optional; the hand-maintained bilingual
    `docs/management_summary.md` is never overwritten by generated
    artifacts.
19. **Probe-first rollout (unit v0.1.1):** the first bounded work unit is
    a slim CLI slice — `db init/status`, `source load/list`, `probe
    run/report` — nothing else. The full command surface (ARCHITECTURE.md)
    is designed ahead and implemented progressively (M0 probe → M1
    frame/sample → M2 acquire/parse → M3 corroborate/analyze → M4
    report). Probing is the Phase-0 instrument: the source census converts
    OPEN register rows into verified access metadata and provisional
    frame inputs before any sampling design is frozen.
20. **Probe entities & anchor promotion:** probing records (`probe_run`,
    `probe_finding`) carry full provenance like every other record; census
    counts are **provisional** —     promotion to `population_anchor` /
    `frame_stratum` is a manual method decision, never automatic (catalog
    coverage bias is real). Probing obeys the DATA_SOURCE.md scraping
    discipline.
21. **Operator layer (queued unit v0.1.2):** the stable operator
    entrypoint is a repo-root `Makefile` (GNU make, stock Slackware) —
    one target per `leadhs` call; pipeline targets (`setup`, `probe`,
    `report`, `census`) orchestrate only until the CLI grows the
    matching commands — pipeline logic belongs in the CLI long-term,
    make stays a thin wrapper (refines D2). Pipeline parameters are
    make variables with documented defaults until milestone M1, when a
    committed config file joins (one config migration, not two;
    parameters still land per-run in the DB per D2). Costly network
    operations (`probe` over all actives, `census`) require explicit
    confirmation (`GO=1`) — the operational form of the census
    go-ahead discipline; wiping local state (`clobber`) is gated the
    same way. CLI operability principles: bare group invocation prints
    help; an uninitialized database yields a guided error ("run
    `make setup`"), never a `bug:` label; strict exit-code conformance
    0/1/2/3/130 (click usage errors → 1); doctor is the preflight gate
    in every pipeline recipe.
22. **Report routing:** generated intermediates go to `data/report/`
    (gitignored, beside the DB, regenerated freely); publishing into
    `docs/report/` (committed) is an explicit act (`make
    report-publish`). `docs/report/` holds published finals only.
    (Refines D18; `management_summary.md` protection unchanged.)
23. **Multilingual documentation (i18n):** English is canonical; DE/FR
    translations live in sibling files with a language suffix
    (`README.de.md`, `README.fr.md`, `METHODOLOGY.de.md`, …) next to the
    English original, with frontmatter `language`, `translation_of`,
    `source_updated` and a language-switcher line. Binding term map:
    `docs/terminology.md` (official act/institution names never
    re-translated; SR/CELEX cites identical across languages). Tranche 1:
    README, METHODOLOGY, DATA_SOURCE. Planning/design/implementation
    documents remain EN-only. Substantive EN edits update translations in
    the same change set or leave `source_updated` behind as a visible
    drift marker.
24. **Distribution & portability (2026-09-11):** `leadhs` ships as a
    standard wheel installed via a managed interpreter (`uv tool
    install`/pipx) for the author and technical peers; wheels as
    GitHub release assets — no public PyPI footprint (commissioning
    context stays implicit). Pure-Python core is a portability policy
    (optional native tools runtime-detected via `leadhs doctor`);
    Docker/AppImage/bundling rejected; PyInstaller per-OS builds
    recorded as contingency only. Detail: ARCHITECTURE.md (D10/D11).
25. **Source-report structure & transparency (2026-09-11):** the
    census report presents structured per-source metadata
    (identification, access, content, counts, availability,
    provenance) plus a cross-source summary matrix, in md/csv/json;
    run status and notes are visible; section titles state "source
    feasibility" — never product or lead counts (M2+). Refines D22.
    Detail: DATA_SOURCE.md (census metadata set).
26. **M0 close-out lives in v0.1.2 (2026-09-11):** census completion
    (parameter fixes, catalog-level probes, manual records, metric
    additions where required) is delivered by unit v0.1.2 together
    with the operator layer and executed through it; the v0.1.1
    PHASE08 feasibility pass (2026-09-11) is its empirical record.
    Supersedes the same-day census-first sequencing decision.
27. **Product data only in tool, database and reports (2026-09-11;
    scope correction, supersedes D14):** the `leadhs` tool, the
    evidence database and all generated reports carry product data
    only — no legal-category dimension, no compound legal-status or
    Swiss-relevance fields, no legal-coded signal lookups, no
    legal-text documents in the raw store. Lawful/illegal assessment
    and Swiss-ban relevance are analytical conclusions drawn in the
    study documentation (10_STRATEGY/LEAD_SDS.md, METHODOLOGY
    regulatory frame), never database fields or report sections.
    The LG source rows stay in the register (inactive, as built) and
    never reach reports by construction — reports draw from probe
    views, and LG rows carry no probe runs. Legal-text verification
    remains a pure documentation workstream outside the tool.
28. **Product-first census; register carries product sources only
    (2026-09-11; user direction, refines D25, applies D27 to the
    register):** the census report answers exactly two questions —
    (Q1) how many paint/varnish products each registered source
    exposes, where "products observed" = distinct product listings
    found in a polite walk, a floor never a market total; and (Q2)
    for how many of them SDS-type documentation is reachable. Trade
    statistics are volume context only: trade rows (`records_hs*`)
    count tariff-line flows, never products. The tool register slims
    to product sources (CS-1, CS-2, PE-1..4, ST-1..3 — nine rows);
    the LG/LI rows leave the tool (migration 0004 prunes the rows and
    any runs/findings recorded against them), and their context
    remains in the 10_STRATEGY documents. The od8 per-source
    feasibility sections are superseded by: the two numbers up front,
    one product-first matrix, the execution log, compact per-source
    blocks, legend — mechanics unchanged (single DB-only assembly,
    md/csv/json; R4 provenance; GO=1 discipline; P7 counts from the
    DB only). Access checks (robots/terms/rate) stay in the database
    and appear as one line per source. PE probing gains
    `products_listed` / `doc_links_seen` (category walk depth ≤ 3,
    page budget); CS-2 per-HS parameterized queries unchanged. Census
    execution (v0.1.2 PHASE07) re-sequenced after the rework:
    verified on one or two sources, then full `GO=1 make census`
    (user-approved 2026-09-11).
29. **v0.1.3 refocus — data-landscape map first (2026-09-12; user
    direction):** before any sizing or sampling, the study needs a
    general map of the data landscape — what is available from which
    source, at what scale, with what access to specifications —
    deliberately coarse ("don't go into detail"); legal references
    and legal data are of no concern in this unit (D27/D28
    discipline). Unit v0.1.3 becomes the data-landscape mapping
    unit: channel enumeration, census-walk extension
    (`products_listed` / `doc_links_seen`), coarse SPIN/PCN/PRODCOM
    priors, latest-year trade context, and one cross-source
    availability map answering Q1 (products identifiable under the
    HS headings, observed floor) and Q2 (spec documents reachable).
    The sampling-frame apparatus (stratification, seeded draw,
    precision targets), the config-file migration and the full
    historical trade import defer to a later unit, chosen via the
    unit's frame-decision bridge. Strategy DRAFT; converges after
    the v0.1.2 census execution.
30. **Three-number deliverable (2026-09-12; user ratification — "this
    is the TOTAL PROJECT"):** the unit's product is the triad
    **N1** market size (paint products on the EU market, HS 3208+3209 —
    REACH registers substances, not products; anchors: ECHA PCN
    statistics as official proxy, CEPE industry structure, PRODCOM
    producer counts; manual records on ST-1/ST-3, provenance-pinned),
    **N2** the total data pool (Σ `products_listed` over the enumerated
    register — products with any reachable listing), **N3** the
    detailed-data pool (Σ `doc_links_seen` — SDS/TDS reachable, per
    channel). Everything else stays but is not the focus. The
    seed-register census executed 2026-09-12 stands as baseline (3 done
    / 1 blocked / 3 failed; `db audit` clean; CS-1 = server-side TLS
    wall confirmed via curl handshake_failure — honest-UA discipline
    holds, no browser impersonation; coop.ch 403 bot wall;
    spin2000.net timeout; example.invalid = the PE-3 placeholder).
    PHASE02's remainder re-scopes to manual `census_status` records +
    the real sweep over the enumerated register (PHASE06). Priority:
    PHASE01 walk counters + PHASE03 enumeration pulled ahead.
    Enumeration bucket caps: MFR ≤12, CH-DIY ≤4, EU-DIY ≤5, MARINE ≤5,
    ART ≤6; B2B portals carried OPEN (no confirmed portal — the PE-3
    placeholder defers to candidate identification at review). Version
    0.1.3 was bumped early at user request (LOG 2026-09-12); PHASE03
    step 1 is verification-only.
31. **Access census; no-scrape reconnaissance; EU-only (2026-09-12;
    user clarification on D29/D30):** the triad stands, re-weighted —
    N1 ("how many are there") is accepted as an estimate and is not
    the unit's operational target; the core is **access coverage**:
    N2 — to how many products do we have access in some form — and
    N3 — for how many can we get detailed data, and for how many an
    MSDS. Method constraint: sound out the data landscape WITHOUT
    starting to scrape — reconnaissance level only (robots/terms,
    existence and shape of API/download endpoints, sitemap presence
    and product-URL counts via a single structured fetch, manual-web
    checks); catalog walks and any product-level collection defer
    until an explicit go. Count-bearing statistical sources (SPIN,
    PCN, PRODCOM/SBS, national product registers) carry the
    measurable part of N2/N3; web channels are characterized, not
    walked. Source discovery is first-class: the register is expected
    to need more / different EU sources — new class AS (CEPE +
    national association member lists; national product registers
    with public statistics) alongside activating ST-1/ST-3. Market
    scope: the Swiss market is of little concern — metrics are
    EU-only (CS-1 and CH-DIY seeds leave the register); Switzerland
    stays the regulatory frame of the study and nothing more. HS 3213
    demotes from full census (D13) to a low-priority annex, worked
    only if free capacity. Deliverable emphasis (user): the report
    must show LARGE NUMBERS — magnitudes of paints on the market and
    data availability for them — not sparse tables. The clarification
    materializes as the new minor-version unit **v0.2.0**
    (`v0.2.md`, numbers-first); v0.1.3 stays FROZEN with a
    supersession note — its walk-based tape is not executed (the
    machinery idles).

## OPEN ITEMS

- CLOSED 2026-09-12 (scope, D31): EZV/swiss-impex — Swiss market
  metrics dropped (EU-only); the TLS handshake failure is documented
  in the census baseline; no further work.
- OPEN: current consolidated ChemRRV Anhang 2.8 (SR 814.81) wording — the
  0.01% threshold, treated articles, and any exceptions verified only on the
  2005 snapshot; verify on fedlex.
- OPEN: current consolidated VIPaV (SR 946.513.8) incl. Art. 16 body text
  and FR wording (fedlex is JS-gated; needs browser/scout extraction).
- OPEN: OJ reference of the 17 Mar 2022 Commission implementing decision
  refusing DCL Corporation (NL) B.V.'s 8 lead-chromate authorisation uses.
- OPEN (high priority, empirical): lead driers (octoate/naphthenate) in
  current EU alkyd paints — neither presence nor absence documented; first
  target of the SDS sampling pilot.
- OPEN (soft): confirm SECO's "Art 2a(1)" ≙ Art. 2 Bst. a Ziff. 1 in writing
  only if the mapping becomes load-bearing; do not build on the deletion
  scenario.
- OPEN/NON-BLOCKING: Swiss legal dossier — ChemO/ChemG restriction status of
  lead compounds in paints; third-country import control. (MRA coverage
  dropped from scope 2026-09-10: separate THG instrument, not this study.)
- OPEN (soft): BBL as requester/owner of the lead exception (per
  commissioning context 2026-09-10) — verify against public record (e.g.
  the 2010 VIPaV explanatory report/Botschaft) before naming BBL in any
  deliverable.
- CLOSED 2026-09-12 (scope, D31): Swiss product-notification landscape
  and BFS producer statistics — Swiss market metrics dropped
  (EU-only); the Swiss layer stays as regulatory framing only
  (LEAD_SDS.md, METHODOLOGY regulatory frame).
- OPEN/NON-BLOCKING: ECHA PCN universe totals + EuPCS paint share (EU context).
- OPEN/NON-BLOCKING: SPIN Access DB extraction; PRODCOM sold production 20.30.1x.
- OPEN: verify CAS for lead naphthenate (61790-14-5?) and lead neodecanoate
  (27253-29-8?) against ECHA EC inventory before freezing the dictionary.
- OPEN: artists' colours vs REACH Annex XVII entries 16/17 — the
  member-state permit mechanism (ILO C13) practice across NL/IT/DE/FR; no
  ECHA guidance document retrieved yet.
- OPEN: FR/IT red-lead primer retail ("minium de plomb"/"minio rosso") —
  unverified; engine capacity, not evidence absence.

## ROADMAP (strategy altitude)

- Phase 0 — close gaps: verify current legal
  texts (ChemRRV Anhang 2.8, consolidated VIPaV); document the CdD
  governance chain for the lead exception from public sources (requester/
  owner, review procedure, 2010 inception record); 2022 refusal OJ ref;
  PCN stats; SPIN query; PRODCOM; catalog counts — via the v0.1.1 source
  census (`leadhs probe`, D19): counts per source, access constraints,
  provisional population anchors. Census go granted 2026-09-11;
  feasibility pass executed the same day (gaps: CS-1 fetch, CS-2
  query params, ST-2 fetch, PE catalog level, manual sources). v0.1.2
  (D26) is the census close-out — full source probing, structured
   source reports, operator layer — and delivers the census through
  `GO=1 make census`.
 User review of the 2026-09-11 report output reframed the census
 product-first (D28): the report now leads with the two study numbers
 (products available; products with reachable SDS), trade rows demote
 to volume context, and the register slims to product sources. Unit
  v0.1.3 (DRAFT, `v0.1.3.md`, refocused 2026-09-12 per D29) turns the
  census floors into the data-landscape map — availability, scale and
  spec access per source, the two study numbers as measured floors;
  the sampling-frame apparatus defers until the map justifies it.
 The 2026-09-12 user clarification (D31) turns the landscape work
 into unit v0.2.0 — market scale & data availability, numbers-first,
 no-scrape reconnaissance, EU-only (`v0.2.md`).
- Phase 1 — pilot: freeze lead dictionary + SDS scrape/parsing on 1–2 strata
  (lead-driers stream first); validate hit-rate prior and CN-assignment
  heuristics; build the `leadhs` CLI skeleton (acquire → ingest → parse →
  sample → report) as the pilot vehicle (skeleton started in v0.1.1 —
  probe era; acquire/ingest/parse land here).
- Phase 2 — frame build + stratified draw + document collection at full n;
  run the HS 3213 artists' colours census annex in parallel.
- Phase 3 — cross-document corroboration and quality assurance (replaces
  laboratory validation).
- Phase 4 — analysis; decision-makers' discussion basis; database freeze.

## Topic index

- `METHODOLOGY.md` — population, frame, stratification, sampling, corroboration
- `LEAD_SDS.md` — compounds, legal status, SDS feasibility, prior studies
- `DATA_SOURCE.md` — source register, access, provenance & scraping discipline
- `DATA_MODEL.md` — evidence-database schema (products, SDS findings, runs)
- `ARCHITECTURE.md` — pipeline, CLI (`leadhs`), reporting, distribution &
  portability
- `charts/` — rendered diagrams in active use (system components,
  lead decision tree, probe process); index and regeneration:
  `charts/README.md`; superseded charts archived under
  `_archive/10_STRATEGY/charts/`

## Active unit

- `v0.1.1.md` — source probing (slim CLI): db/source/probe tools; the
  Phase-0 instrument. Strategy converged; Design may proceed for the
  slim scope.
- `v0.1.2.md` — census close-out (full source probing, structured
  source reports, operator layer per D25/D26): strategy converged
  (D21/D22/D25/D26); unit doc LIVE.
- `v0.1.3.md` — data-landscape map (refocused 2026-09-12, D29):
  what is available from which source, at what scale, with what spec
  access — Q1/Q2 as measured floors per source; coarse priors,
  latest-year trade context, frame-decision bridge. Strategy
  converged 2026-09-12 on D30 (three-number deliverable N1/N2/N3);
  design and implementation plans live; build follows the prepared
  tape. 2026-09-12, D31: superseded in part by v0.2.0 — walk
  execution idles, unit stays FROZEN; see `v0.2.md`.
- `v0.2.md` — market scale & data availability (the numbers unit,
  v0.2.0; the D31 strategy turn): N1 market-size estimate from
  official statistics, N2/N3 access coverage (registers +
  reconnaissance), AS-class source discovery, numbers-first report.
  Strategy DRAFT — converges on user validation.
- v0.1 (feasibility & study design) remains the foundational strategy
  pass; its legal-verification open items stay in OPEN ITEMS above.

## Readiness for Design

Split. For unit v0.1.1 (slim probe CLI): yes — strategy is converged
(scope, entities, discipline fixed in D19/D20, DATA_MODEL.md,
ARCHITECTURE.md); Design may proceed. For the full pipeline (frame,
sampling, scraping at scale): not yet — freeze awaits the v0.1.1 probe
results (source counts, swiss-impex format, SDS corpus quality) and the
legal-text verification items in OPEN ITEMS.

For unit v0.1.2 (census close-out): strategy converged
(D21/D22/D25/D26); Design proceeds on od1–od7 plus od8 (report
content) and the OD-A decision (per-HS metrics vs M1 deferral).

For unit v0.1.3: yes — strategy converged 2026-09-12 on D30 (three-
number deliverable; caps and matrix columns pinned against the
2026-09-12 baseline census). Design (pe1–pe7) and phase plans
(PHASE01–07) exist; build executes on explicit go. The frame unit
stays deferred behind the bridge.

For unit v0.2.0: strategy DRAFT (the D31 turn, 2026-09-12) —
converges on user validation of the numbers-first framing; Design
then covers the recon probe shape, AS register rows + migration, the
CS-2 parser/persistence fix and the numbers-report layout.
