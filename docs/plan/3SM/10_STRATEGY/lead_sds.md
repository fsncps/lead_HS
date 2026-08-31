---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Lead identification via SDS — compounds, legal status, feasibility

## Abstract

This document collects what is known about lead in paints and where the law
stands. Lead compounds appear in paints as colour pigments (e.g. lead
chromate yellows/reds, white lead), rust-protection additives (red lead) and
drying agents in solvent-based alkyd paints (lead octoate). EU law bans
several of them in paints or for consumer use, but rust-protection additives
and drying agents remain legal; whether Swiss law mirrors each EU rule is
being verified separately (legal dossier workstream). Safety data sheets
must list hazardous ingredients above 0.1% — so they reveal deliberately
added lead, but not trace contamination. The document also lists earlier
studies (mostly outside Europe) that calibrate expectations, and the exact
chemical identifiers used to search the sheets.

## Lead-compound dictionary (v0.1)

| CAS | Name / synonym | C.I. | Function | Segments | EU legal status | SDS-visible |
|---|---|---|---|---|---|---|
| 7758-97-6 | Lead chromate (chrome yellow) | PY34 family | pigment | industrial, road-marking | Annex XIV #10, sunset 2015-05-21; App.2 CMR ban | ≥0.1% |
| 1344-37-2 | Lead sulfochromate yellow | PY34 (C.I. 77603) | pigment | enamels | Annex XIV #11; App.2 | ≥0.1% |
| 12656-85-8 | Lead chromate molybdate sulfate red | PR104 (C.I. 77605) | pigment | industrial topcoats | Annex XIV #12; App.2 | ≥0.1% |
| 1314-41-6 | Red lead / minium (Pb₃O₄) | PR105 | anticorrosive | marine/steel primers | **no restriction** | ≥0.1% (Repr 1A route) |
| 1317-36-8 | Litharge (PbO) | 77577 | intermediate | drier precursor | no restriction | ≥0.1% |
| 1319-46-6 | White lead (basic lead carbonate) | 77597 | pigment (historic) | art/restoration | **Annex XVII #16: banned in paints** (art derogation) | n/a |
| 598-63-0 | Lead carbonate | — | pigment (historic) | — | Annex XVII #16 | n/a |
| 7446-14-2 / 15739-80-7 | Lead sulfate / basic lead sulfate | 77630 | extender, primers | anticorrosive | **Annex XVII #17: banned in paints** | n/a |
| 301-08-6 | Lead octoate (bis(2-ethylhexanoate)) | — | **drier** | alkyds (3208) | no restriction verified | ≥0.1% |
| 61790-14-5* | Lead naphthenate | — | drier | alkyds/inks | unverified | ≥0.1% |
| 27253-29-8* | Lead neodecanoate | — | drier | industrial alkyds | unverified | ≥0.1% |

(*) CAS to verify against ECHA EC inventory before dictionary freeze.
Related: non-lead chromate anticorrosives (strontium chromate etc.) are also
Annex XIV (sunset 2019) — screening flag when present.

## EU legal frame (verified)

- Annex XVII 16/17: lead carbonates/sulfates banned **in paints**; MS art-restoration derogation.
- Annex XIV 10–12 + entries 28–30: lead chromates post-sunset, consumer CMR ban; authorisations partially annulled (Sweden v Commission, GC 2019; case numbers T-706/17, T-707/17 unverified).
- Entry 63: lead ≥0.05% in mouthable consumer **articles** (paint is a mixture → context, not constraint); PVC amendment 2023/1422 unverified.
- SDS cutoffs (Reg (EU) 2020/878, Annex II REACH): CMR 1A/1B ≥ 0.1% must be listed in Sec. 3; OEL-listed substances must be listed (no explicit % for that route); ranges permitted. SDS free of charge on request (Art. 31(8)).

## Swiss context (OPEN — legal dossier workstream, verify before asserting)

- Switzerland is not in the EU/EEA; REACH/CLP do not apply directly. Swiss
  chemicals law (ChemG/ChemO) was substantially aligned with REACH/CLP in
  the 2015 harmonization — the current coverage of the EU lead restrictions
  above (Annex XVII 16/17, XIV 10–12, entries 28–30/63) in Swiss law is
  **to be verified against ChemO/ChemV primary sources**.
- Switzerland is not part of the EU PCN system; its own poison-centre and
  product-notification landscape (and any public statistics from it) is an
  open research item.
- EU–CH Mutual Recognition Agreement: sectoral coverage relevant to paints
  to be verified.
- Swiss-market SDS are typically available in DE/FR/IT/EN from producer
  portals — the pipeline must be multilingual.

## Feasibility assessment

- **Visible:** intentionally added classified lead compounds ≥ 0.1% (pigments at % levels; driers typically ≥0.1% Pb — flagged as domain inference).
- **Invisible:** sub-0.1% and impurity lead by design; empirical SDS quality is mediocre (NO 2014: 320 SDS generic/incomplete; artificial-stone 2022: relevant constituents under-reported) → treat absence of evidence carefully; staleness (<2021 format) and "may contain" language = red flags.
- **No laboratory in this project:** the blind spots above cannot be bounded
  experimentally. Mitigation is document-only corroboration (see
  `methodology.md`): cross-check positives against TDS, labels, retailer
  listings, older SDS versions, cross-market brand variants; report
  contradictions as findings; carry an explicit limitations section in the
  final discussion basis.
- **Availability:** manufacturer/brand sites + B2B portals (scrape; DE/FR/IT/EN); no public EU SDS repository; PCN submissions not public; UFI in Sec. 1.1 as join key.
- **CN assignment from SDS:** medium (aqueous?) + binder (acrylic/vinyl/polyester/other) → CN8; borderline: ≥50%-solvent polymer solutions (3208 10/20 vs 90), hybrids.

## Prior studies (calibration)

- **No EU/EEA-wide or Swiss lead-in-paint market survey exists** — the gap this study fills.
- Mexico 2026 (213 paints, lab): 55% >90 ppm; 91% of leaded ≈ lead chromate (Pb:Cr 4:1); 12 leaded products labelled "no lead". DOI 10.1093/annweh/wxag023
- IPEN global campaign (59 countries, >5,000 paints, lab): high prevalence in developing markets; country database Oct 2024. ipen.org/our-work/lead-paint
- Kumar et al. 2018 review: often >10,000 mg/kg in LMIC paints. DOI 10.1016/j.envint.2018.08.052
- WHO 2024: 48% of countries have binding lead-paint controls.
- Working hypothesis (to test): Swiss consumer decorative ≈ 0% intentional lead; single-digit % in professional/industrial 3208 strata; higher in third-country imports.

## REFERENCES

Legal: consolidated REACH CELEX 02006R1907-20221014; Reg (EU) 125/2012; Reg (EU) 2020/878; Reg (EU) 2015/628 — all via EUR-Lex canonical URLs + Wayback snapshots (accessed 2026-08-31). Studies: DOIs and OpenAlex records as cited above. SDS quality: DOI 10.2478/s13382-014-0302-8; DOI 10.1093/annweh/wxac020; DOI 10.1002/ajim.20613.
