"""CS adapter — export/API sources (Eurostat Comext DS-045409 et al.).

v0.2.3 PHASE02 split (TODOS watch item): one adapter class per module;
the shared helpers live in ``_common.py``; the public import surface
stays ``leadhs.probe.adapters`` (package __init__ re-exports).
"""

from __future__ import annotations

import csv
import io
import json
import re

from ...jsonstat import JsonstatError, decode as jsonstat_decode, one_dim as jsonstat_one_dim, sum_pairs as jsonstat_sum_pairs
from ...models import FindingDraft, ProbeResult, SourceRef, StagedTradeRow
from ._common import UnexpectedFormat, _doc, _log

_EXPECTED_EXPORT_COLUMNS = {"hs_code", "year", "partner"}
_JSON_LIST_COUNTS = ("value", "obs", "records", "observations", "data")

# od9: parameterized CS-2 query — documented constants with defaults
# fixed here (pinned at census execution 2026-09-12 against the live
# DS-045409 API: time dimension `time`, import flow code `1`,
# indicators QUANTITY_IN_100KG / VALUE_IN_EUROS); the parameters land
# in run.parameters_json via ProbeResult.parameters, and every response
# is archived as a document (verification artifact).
_CS_QUERY_DEFAULTS = {
    "format": "JSON",
    "freq": "A",
    "time": "2024",
    "flow": "1",
    "reporter": "EU27_2020",
}
_HS_CODES = ("3208", "3209", "3213")
# nu2 aggregation: the four trade-sum anchors ride HS 3208/3209 only
# (3213 stays the census annex).
_AGG_HS_CODES = ("3208", "3209")
_CS_AGG_INDICATORS = (
    ("kg", "QUANTITY_IN_100KG"),
    ("eur", "VALUE_IN_EUROS"),
)
# v0.2.2 W1 batch: DS-045409 extra-EU flow codes (verified against the
# live API in v0.2.0: import = 1); intra-EU flow codes remain OPEN (design)
_CS_BATCH_FLOWS = ("1", "2")
_CS_BATCH_INDICATORS = _CS_AGG_INDICATORS


def _query_url(base: str, params: dict) -> str:
    from urllib.parse import urlencode

    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode(params)}"


def _agg_params(hs: str, indicator: str, year: str) -> dict:
    """Full-year import aggregation query (nu2): flow + resolved year
    land in run.parameters_json; with reporter/product/flow/indicators/
    time pinned, partner is the only free dimension (all partners)."""
    return {
        **_CS_QUERY_DEFAULTS,
        "product": hs,
        "indicators": indicator,
        "time": year,
    }

class CSAdapter:
    key = "CS"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "CS"

    def _is_query_api(self, source: SourceRef) -> bool:
        return source.access_method_code == "api"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
        if ctx.mode == "capability":
            # v0.2.2 W1: the per-CN8 batch replaces the census aggregation
            # in capability mode (the run composes, fu3)
            if self._is_query_api(source):
                return self._probe_cn8_batch(source, ctx)
            return ProbeResult()
        if ctx.dry_run:
            if self._is_query_api(source):
                for hs in _HS_CODES:
                    ctx.fetcher.plan(_query_url(source.url, {**_CS_QUERY_DEFAULTS, "product": hs}))
                # nu2/e7: the aggregation queries are part of the plan
                for hs in _AGG_HS_CODES:
                    for _, indicator in _CS_AGG_INDICATORS:
                        ctx.fetcher.plan(_query_url(source.url, _agg_params(hs, indicator, _CS_QUERY_DEFAULTS["time"])))
            else:
                ctx.fetcher.plan(source.url)
            return ProbeResult()
        if self._is_query_api(source):
            return self._probe_query_api(source, ctx)
        resp = ctx.fetcher.get(source.url)
        _log(ctx, "cs_get", url=source.url, status=resp.status_code)
        docs = [_doc(source.url, resp, retrieval_method_code=source.access_method_code or "scrape")]
        findings = []
        notes = []
        ct = resp.headers.get("Content-Type", "")
        text = resp.text
        if "csv" in ct.lower() or (text.lstrip()[:1] in ('"', ";") and "," in text[:500]):
            findings += self._probe_csv(source, resp, ctx, docs, notes)
        elif "json" in ct.lower() or text.lstrip()[:1] in ("{", "["):
            findings += self._probe_json(source, resp, ctx, docs, notes)
        else:
            findings.append(FindingDraft(metric_code="format", method_code=source.access_method_code or "scrape", value_text="web UI (HTML); export via UI, layout to confirm"))
            findings.append(FindingDraft(metric_code="granularity", method_code=source.access_method_code or "scrape", value_text="to confirm at manual review (probe)"))
            findings.append(FindingDraft(metric_code="free_access", method_code=source.access_method_code or "scrape", value_numeric=1, unit_code=None))
            notes.append("landing page reached; export mechanics to confirm manually")
        return ProbeResult(documents=docs, findings=findings, notes=notes)

    def _probe_query_api(self, source: SourceRef, ctx) -> ProbeResult:
        """od9: one parameterized JSON query per HS heading; each response
        archived; empty result set is an honest 0. v0.2.0 (nu2): plus the
        full-year import aggregation for HS 3208/3209 — trade_kg/eur sums
        via the JSON-stat decoder (e2/2A)."""
        docs, findings, notes = [], [], []
        query_params = {}
        for hs in _HS_CODES:
            params = {**_CS_QUERY_DEFAULTS, "product": hs}
            query_params[hs] = params
            url = _query_url(source.url, params)
            resp = ctx.fetcher.get(url)
            _log(ctx, "cs_query", url=url, status=resp.status_code, hs=hs)
            docs.append(_doc(url, resp, retrieval_method_code="api"))
            try:
                data = json.loads(resp.text)
            except ValueError:
                raise UnexpectedFormat(
                    f"HS {hs}: expected JSON but content not parseable",
                    partial=ProbeResult(documents=docs, findings=findings),
                    url=url,
                )
            is_jsonstat = isinstance(data, dict) and "id" in data and "size" in data
            findings.append(
                FindingDraft(
                    metric_code="format",
                    method_code="api",
                    value_text="JSON-stat dataset" if is_jsonstat else "JSON (API)",
                )
            )
            rows = self._rows_of(data)
            findings.append(
                FindingDraft(
                    metric_code=f"records_hs{hs}",
                    method_code="api",
                    value_numeric=len(rows),
                    unit_code="count",
                    document=docs[-1],
                    notes=f"query params: {json.dumps(params, sort_keys=True)}",
                )
            )
            notes.append(f"HS {hs}: {len(rows)} rows")
        findings += self._aggregate(source, ctx, docs, query_params, notes)
        return ProbeResult(documents=docs, findings=findings, notes=notes, parameters={"query": query_params})

    def _probe_cn8_batch(self, source: SourceRef, ctx) -> ProbeResult:
        """v0.2.2 W1 (e6/fu10): per in-scope CN8 code × flow × indicator,
        one parameterized DS-045409 query; payloads decoded via the
        jsonstat module (multi-dimension: declarant × period) →
        StagedTradeRow drafts. Per-query fetch timeout/retry ride the
        standard fetcher. Batch shape pinned here: 13 codes × 2 extra-EU
        flows × 2 indicators (52 payloads); intra-EU flow codes remain
        OPEN (design) and join the batch once verified. Trade rows stage
        with source_id + run_key + doc hash provenance (fu2)."""
        from ...staging import CN8_DICT

        docs, notes = [], []
        query_params = {}
        staged = []
        base_year = _CS_QUERY_DEFAULTS["time"]
        for cn8, heading, kind, label in CN8_DICT:
            for flow in _CS_BATCH_FLOWS:
                for unit_name, indicator in _CS_BATCH_INDICATORS:
                    params = {**_CS_QUERY_DEFAULTS, "product": cn8, "flow": flow, "indicators": indicator}
                    key = f"{cn8}_f{flow}_{unit_name}"
                    query_params[key] = params
                    url = _query_url(source.url, params)
                    if ctx.dry_run:
                        ctx.fetcher.plan(url)
                        continue
                    resp = ctx.fetcher.get(url)
                    _log(ctx, "cs_batch", url=url, status=resp.status_code, cn8=cn8, flow=flow, unit=unit_name)
                    docs.append(_doc(url, resp, retrieval_method_code="api"))
                    try:
                        data = json.loads(resp.text)
                    except ValueError:
                        raise UnexpectedFormat(
                            f"CN8 {cn8} f{flow} {unit_name}: expected JSON-stat but content not parseable",
                            partial=ProbeResult(documents=docs),
                            url=url,
                        )
                    try:
                        decoded = jsonstat_decode(data)
                    except JsonstatError as exc:
                        raise UnexpectedFormat(str(exc), partial=ProbeResult(documents=docs), url=url)
                    for labels, value in decoded:
                        if labels.get("indicators") not in (None, indicator):
                            continue
                        staged.append(
                            StagedTradeRow(
                                cn8=cn8,
                                flow=flow,
                                declarant=labels.get("declarant"),
                                partner=None,
                                year=labels.get("time") or base_year,
                                kg=value * 100.0 if indicator == "QUANTITY_IN_100KG" else None,
                                eur=value if indicator == "VALUE_IN_EUROS" else None,
                                document=docs[-1],
                            )
                        )
        notes.append(
            f"CN8 batch: {len(CN8_DICT)} codes x {len(_CS_BATCH_FLOWS)} flows x "
            f"{len(_CS_BATCH_INDICATORS)} indicators = {len(query_params)} queries; "
            f"{len(staged)} staged trade rows"
        )
        result = ProbeResult(documents=docs, staged_trade=staged, notes=notes)
        if not ctx.dry_run:
            result.parameters = {"query": query_params}
            if ctx.staging is not None and {r.cn8 for r in staged} >= {c[0] for c in CN8_DICT}:
                # U6: every in-scope code delivered at least one row — the
                # seeded dictionary is confirmed against live responses
                from ...staging import mark_dict_verified

                mark_dict_verified(ctx.staging)
        return result

    def _aggregate(self, source, ctx, docs, query_params, notes) -> list:
        """nu2: per HS × indicator, full-year import sums with a bounded
        year step-back (e7): empty → previous year, max 3 tries; exhausted
        → documented-blocked. Partner tops + supplementary units land in
        the finding notes; raw JSON is archived."""
        findings = []
        base_year = int(_CS_QUERY_DEFAULTS["time"])
        for hs in _AGG_HS_CODES:
            for unit_name, indicator in _CS_AGG_INDICATORS:
                year = base_year
                tries = 0
                total, tops = None, []
                while tries < 3:
                    params = _agg_params(hs, indicator, str(year))
                    query_params[f"{hs}_{unit_name}_{year}"] = params
                    url = _query_url(source.url, params)
                    resp = ctx.fetcher.get(url)
                    _log(ctx, "cs_agg", url=url, status=resp.status_code, hs=hs, unit=unit_name, year=year)
                    docs.append(_doc(url, resp, retrieval_method_code="api"))
                    try:
                        data = json.loads(resp.text)
                    except ValueError:
                        raise UnexpectedFormat(
                            f"HS {hs} {unit_name}: expected JSON-stat but content not parseable",
                            partial=ProbeResult(documents=docs, findings=findings),
                            url=url,
                        )
                    try:
                        pairs = jsonstat_one_dim(data)
                    except JsonstatError as exc:
                        raise UnexpectedFormat(str(exc), partial=ProbeResult(documents=docs, findings=findings), url=url)
                    if pairs:
                        total, tops = jsonstat_sum_pairs(pairs)
                        if indicator == "QUANTITY_IN_100KG":
                            # the API's supplementary unit is 100 kg —
                            # convert to the metric's kg and say so
                            total = total * 100
                        tops_txt = ", ".join(f"{lab}={val:.0f}" for lab, val in tops)
                        notes.append(
                            f"HS {hs} {unit_name} {year}: sum across partners "
                            f"(indicators={indicator}); top partners: {tops_txt}"
                        )
                        break
                    tries += 1
                    if tries < 3:
                        notes.append(f"HS {hs} {unit_name}: empty for {year} — stepping back a year (e7)")
                        year -= 1
                metric = f"trade_{unit_name}_hs{hs}"
                if total is None:
                    notes.append(f"HS {hs} {unit_name}: no data for {base_year}..{year} — documented blocked (e7)")
                    findings.append(
                        FindingDraft(
                            metric_code=metric,
                            method_code="api",
                            value_numeric=0,
                            unit_code=unit_name,
                            notes=f"empty for {base_year}..{base_year - 2} (step-back exhausted) — query family blocked, verify at od9",
                        )
                    )
                else:
                    unit_note = "; quantity converted from QUANTITY_IN_100KG (×100)" if indicator == "QUANTITY_IN_100KG" else ""
                    findings.append(
                        FindingDraft(
                            metric_code=metric,
                            method_code="api",
                            value_numeric=total,
                            unit_code=unit_name,
                            document=docs[-1],
                            notes=f"flow=1 (import), year={year}, indicators={indicator}; sum across partners; top partners: {tops_txt}{unit_note}",
                        )
                    )
        return findings

    @staticmethod
    def _rows_of(data) -> list:
        # JSON-stat datasets: the record count is the number of queried
        # cells (value object keyed by flat index, e2/2A shape)
        if isinstance(data, dict) and "id" in data and "size" in data:
            value = data.get("value")
            if isinstance(value, dict):
                return list(value.items())
            if isinstance(value, list):
                return value
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in _JSON_LIST_COUNTS:
                if isinstance(data.get(key), list):
                    return data[key]
            for value in data.values():
                if isinstance(value, list):
                    return value
        return []

    def _probe_csv(self, source, resp, ctx, docs, notes):
        reader = csv.reader(io.StringIO(resp.text))
        rows = [r for r in reader if any(c.strip() for c in r)]
        if not rows:
            raise UnexpectedFormat("empty CSV export", partial=ProbeResult(documents=docs, findings=[]), url=source.url)
        header = [c.strip().lower() for c in rows[0]]
        norm = {re.sub(r"[^a-z0-9_]", "", c) for c in header}
        missing = _EXPECTED_EXPORT_COLUMNS - norm
        if missing:
            raise UnexpectedFormat(
                f"export layout missing expected columns {sorted(missing)} (got {header})",
                partial=ProbeResult(documents=docs, findings=[]),
                url=source.url,
            )
        findings = [
            FindingDraft(metric_code="format", method_code="download", value_text=f"CSV; columns: {', '.join(header)}"),
            FindingDraft(metric_code="export_rows", method_code="download", value_numeric=max(0, len(rows) - 1), unit_code="count"),
            FindingDraft(metric_code="free_access", method_code="download", value_numeric=1),
            FindingDraft(metric_code="granularity", method_code="download", value_text="CN8 x partner x year (observed columns)"),
            FindingDraft(metric_code="coverage_years", method_code="download", value_text="to confirm (year column present)"),
        ]
        notes.append(f"CSV export checked: {len(rows)-1} rows")
        return findings

    def _probe_json(self, source, resp, ctx, docs, notes):
        try:
            data = json.loads(resp.text)
        except ValueError:
            raise UnexpectedFormat("expected JSON but content not parseable", partial=ProbeResult(documents=docs, findings=[]), url=source.url)
        count = None
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            for key in _JSON_LIST_COUNTS:
                if isinstance(data.get(key), list):
                    count = len(data[key])
                    break
            if count is None:
                for value in data.values():
                    if isinstance(value, list):
                        count = len(value)
                        break
        findings = [
            FindingDraft(metric_code="format", method_code="api", value_text="JSON (API)"),
            FindingDraft(metric_code="free_access", method_code="api", value_numeric=1),
            FindingDraft(metric_code="granularity", method_code="api", value_text="to confirm from JSON structure (probe)"),
        ]
        if count is not None:
            findings.append(FindingDraft(metric_code="export_rows", method_code="api", value_numeric=count, unit_code="count"))
        notes.append("JSON API reached; structure re-check at census")
        return findings
