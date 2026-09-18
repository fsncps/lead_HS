# Lead determination — decision tree

Source of truth: docs/study/METHODOLOGY.md (lead determination,
corroboration) and docs/study/LEAD_SDS.md (feasibility, blind spot).
Rendered with --type decision_tree.

## Decision Tree

- Does SDS Section 3 list a lead compound (CAS/EC/synonym dictionary match)?
  - no → none_listed (≠ lead-free); consistent silence across documents = weak evidence of absence
  - yes → continue
- Is the compound classified (CMR 1A/1B) or OEL-listed, declared ≥ 0.1%?
  - no / below floor → invisible to the SDS method (blind spot: 100–1000 ppm band)
  - yes → continue
- EU legal status of the compound?
  - banned in paints (Annex XVII 16/17) or authorisation refused (Annex XIV chromates) → EU-lawful supply unlikely; anomaly signal; verify + corroborate
  - unrestricted (red lead, lead driers, artists' pigments) → EU-lawful presence possible; continue
- Does the Swiss 100 ppm total-Pb ban plausibly engage?
  - yes → swiss_ban_plausibly_engaged = true; corroborate across documents
  - no / unclear → record finding; continue
- Corroboration across independent documents (TDS / label / listing / older SDS / cross-market)?
  - agrees → confirmed finding
  - contradicts → contradiction is itself a reportable finding
  - consistent silence → weak evidence of absence, reported as such

```
SDS Sec.3 lists lead compound?
   ├─ no ─▶ none_listed (≠ lead-free); weak evidence of absence
   └─ yes ─▶ classified / OEL-listed, ≥0.1%?
        ├─ no ─▶ invisible (blind spot 100–1000 ppm)
        └─ yes ─▶ EU legal status?
             ├─ banned / refused ─▶ anomaly; verify + corroborate
             └─ unrestricted ─▶ Swiss 100 ppm ban engaged?
                  ├─ yes ─▶ corroborate across documents
                  └─ no ─▶ record finding
                             └─ corroboration: agrees / contradicts / silence
```
