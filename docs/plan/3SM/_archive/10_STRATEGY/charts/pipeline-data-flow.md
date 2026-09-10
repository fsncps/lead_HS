# Pipeline data flow

Source of truth: 10_STRATEGY/ARCHITECTURE.md (pipeline stages 0–10) and
10_STRATEGY/METHODOLOGY.md (implementation mapping). Rendered with
--type data_flow.

## Data Flow

- Sources (CS/PE/LG/ST/LI) → probe → probe_run / probe_finding (provisional population anchors)
- Sources → acquire → raw store (data/raw/<source-id>/<sha256>.<ext>)
- raw store → ingest → product / sighting / manufacturer
- product + sds_document → parse → sds_finding + lead_compound
- trade_stat + population_anchor → frame → frame_stratum
- frame_stratum → sample → sampling_run / sample_selection
- sample_selection → screen → screen_status
- sds_finding + corroboration documents → corroborate → corroboration
- frame_stratum + sds_finding + corroboration → analyze → prevalence
- prevalence → report → generated report (DE/FR/EN)

```
Sources ──probe──▶ probe_run/probe_finding ──▶ population_anchor
Sources ──acquire──▶ raw store ──ingest──▶ product/sighting/manufacturer
product+sds_document ──parse──▶ sds_finding + lead_compound
trade_stat+population_anchor ──frame──▶ frame_stratum
frame_stratum ──sample──▶ sampling_run/sample_selection
sample_selection ──screen──▶ screen_status
sds_finding+corroboration ──corroborate──▶ corroboration
frame_stratum+sds_finding+corroboration ──analyze──▶ prevalence
prevalence ──report──▶ generated report (DE/FR/EN)
```
