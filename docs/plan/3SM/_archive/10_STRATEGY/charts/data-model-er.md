# Evidence database — entity relationship

Source of truth: 10_STRATEGY/DATA_MODEL.md (strategy-level entities).
The design-level normalized schema is 20_DESIGN/MASTER/data_model.md.
Rendered with --type entity_relationship.

## Entities

- source: id, class (CS/PE/LG/ST/LI), name, url, access_method, verification_status
- probe_run: id, source_id, mode, status
- probe_finding: id, probe_run_id, source_id, metric, value, unit, method
- manufacturer: id, name, country, type, source_id
- product: id, manufacturer_id, name_base, segment_stratum, cn_code, origin, legal_category
- sighting: id, product_id, url, retailer, date, source_id
- sds_document: id, product_id, url, raw_hash, language, revision_date, parse_status
- sds_finding: id, sds_document_id, cas_rn, compound_id, concentration_type, review_status
- lead_compound: cas_rn, ec_number, name, synonyms, function_class, eu_legal_status
- corroboration: id, product_id, finding_ref, document_type, agrees, source_id
- trade_stat: id, year, cn8, partner_country, flow, value_chf, source_id
- population_anchor: id, anchor, value, unit, year, source_id
- frame_stratum: id, stratum, origin, population_estimate, method, source_id
- sampling_run: id, scope, parameters_json, seed, status
- sample_selection: id, run_id, product_id, stratum, origin, screen_status

## Relations

- source 1—N probe_run
- probe_run 1—N probe_finding
- source 1—N probe_finding
- source 1—N manufacturer
- manufacturer 1—N product
- product 1—N sighting
- product 1—N sds_document
- sds_document 1—N sds_finding
- lead_compound 1—N sds_finding
- product 1—N corroboration
- source 1—N trade_stat
- source 1—N population_anchor
- source 1—N frame_stratum
- sampling_run 1—N sample_selection
- product 1—N sample_selection
- frame_stratum 1—N sample_selection
- probe_finding 1—1 population_anchor (manual promotion, never automatic)

```
source ─1─N─ probe_run ─1─N─ probe_finding ─1─1─ population_anchor
source ─1─N─ trade_stat                    (manual promotion)
source ─1─N─ manufacturer ─1─N─ product ─1─N─ sighting
product ─1─N─ sds_document ─1─N─ sds_finding ─N─1─ lead_compound
product ─1─N─ corroboration
product ─1─N─ sample_selection ─N─1─ sampling_run
sample_selection ─N─1─ frame_stratum ─N─1─ source
```
