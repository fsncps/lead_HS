"""AS adapter — official register capability ingest (ECAT et al.).

v0.2.3 PHASE02 split (TODOS watch item): one adapter class per module;
the shared helpers live in ``_common.py``; the public import surface
stays ``leadhs.probe.adapters`` (package __init__ re-exports).
"""

from __future__ import annotations

import json
import re

from ...models import FindingDraft, ProbeResult, SourceRef, StagedRow
from ._common import (
    UnexpectedFormat,
    _JSON_LIST_COUNTS,
    _delimiter_of,
    _doc,
    _log,
    depth_tier,
    read_csv_rows,
    sniff_kind,
)

# Expected export headers per source — pinned from the v0.2.1 capability
# record (ECAT: company_name / code_value GTIN+EAN / product_or_service_name /
# group_name) or desk analysis; a missing column is a column-drift format
# finding, never a guess (e3). Absent entry = no expectation (generic).
_EXPORT_EXPECTED = {
    "AS-2": ("product_or_service_name", "company_name", "group_name"),
}


def _in_scope_group(group: str) -> bool:
    """The ECAT group-044 (paints & varnishes) row filter — the register
    total is 88,920 across ALL groups; the study counts the paints group
    (16,001 + 1,817 + 20 subset, v0.2.1 record). Group naming pinned at
    W1; until then: the group name mentions paint/varnish/coating."""
    g = group.casefold()
    return any(t in g for t in ("paint", "varnish", "coating", "044", "44"))
# --- AS adapter (register-capability sounding-out, v0.2.1 cap2/cap5) -------


# Column-detection hints for the register shape inspect (i17): the
# capability profile is measured, not declared — a source exposes a
# manufacturer / product-ident / CN8-nomenclature field when its export
# header carries one of these (0/1 flags, nu8 — the mechanism is the
# descriptive cap_cn8_linkage text, never string-matched).
_MANUFACTURER_HINTS = ("manufacturer", "producer", "company", "brand", "organization", "organisation", "org")
_PRODUCT_IDENT_HINTS = ("licence", "ufi", "article", "sku", "gtin", "product_ident", "productid", "ean")
_NOMENCLATURE_HINTS = ("cn8", "cn_code", "hs_code", "nomenclature", "commodity", "cn_code8")
_CN_CODE_RE = re.compile(r"\b(\d{8}|\d{6}|\d{4})\b")
# The study's 13 CN8 codes are deferred to 0008/M1 (cap6) — the adapter
# counts distinct CN-prefixed codes observed and caps at 13, flagging
# the deferral in the finding note (exact 13-code matching is M1 work).
_CN8_REACHABLE_CAP = 13


class ASAdapter:
    key = "AS"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "AS"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
        """Register-capability sounding-out (cap2/cap4): fetch an official
        register export (CSV/API) and inspect its shape against the product
        model. No-ops for non-`capability` modes (C1) so the census/recon
        sweeps are unchanged; manual-access_method sources are
        characterized by `probe record --mode capability`, never here.

        v0.2.2 (W1/W2): a register row with a pinned ``export_url`` runs
        the staged export ingest (fetch → sniff → shared CSV path →
        StagedRow drafts → engine staging + run-close derivation) instead
        of the shape inspect.
        """
        if ctx.mode != "capability":
            return ProbeResult()
        if source.access_method_code not in ("download", "api"):
            return ProbeResult()
        if ctx.dry_run:
            ctx.fetcher.plan(source.export_url or source.url)
            return ProbeResult()
        if source.export_url:
            resp = ctx.fetcher.get(source.export_url)
            _log(ctx, "as_export_get", url=source.export_url, status=resp.status_code)
            docs = [_doc(source.export_url, resp, retrieval_method_code=source.access_method_code)]
            return self._ingest_export(resp, source, docs)
        resp = ctx.fetcher.get(source.url)
        _log(ctx, "as_get", url=source.url, status=resp.status_code)
        docs = [_doc(source.url, resp, retrieval_method_code=source.access_method_code)]
        return self._inspect_register(resp, source, docs)

    def _ingest_export(self, resp, source: SourceRef, docs) -> ProbeResult:
        """Staged export ingest (W1): the sniff gate runs BEFORE any parse
        (e3 — the AS-7 HTML-as-CSV class); the shared CSV path validates
        shape; rows become StagedRow drafts (engine stages them and
        derives the run-close metrics, fu1). A legitimate empty in-scope
        result sets ``staged_zero`` (c2 counted-0), never a format failure."""
        kind = sniff_kind(resp.headers.get("Content-Type"), resp.content[:512])
        if kind == "html":
            findings = [
                FindingDraft(metric_code="format", method_code=source.access_method_code or "download",
                             value_text="HTML landing page — not a CSV/JSON export; export mechanics to confirm"),
            ]
            return ProbeResult(documents=docs, findings=findings,
                               notes=["HTML at the pinned export URL — manual fallback (c1)"])
        if kind not in ("csv", "tsv"):
            raise UnexpectedFormat(
                f"pinned export is {kind}, expected CSV/TSV — layout to re-pin",
                partial=ProbeResult(documents=docs),
            )
        sep = "\t" if kind == "tsv" else _delimiter_of(resp.content.split(b"\n", 1)[0])
        try:
            header, data_rows = read_csv_rows(resp.content, separator=sep, expected=_EXPORT_EXPECTED.get(source.id))
        except UnexpectedFormat:
            raise
        rows, kept, dropped = [], 0, 0
        for raw_row in data_rows:
            record = dict(zip(header, raw_row))
            group = (record.get("group_name") or record.get("group") or "").strip()
            if not _in_scope_group(group):
                dropped += 1
                continue
            kept += 1
            rows.append(
                StagedRow(
                    manufacturer_raw=record.get("company_name") or record.get("manufacturer") or None,
                    ident_raw=record.get("code_value") or record.get("licence_no") or None,
                    ident_hint="code_value (GTIN/EAN)" if record.get("code_value") else "licence_no",
                    name=record.get("product_or_service_name") or record.get("product_name") or None,
                    category_raw=group or None,
                    raw=record,
                    document=docs[0],
                )
            )
        notes = [
            f"export ingest: {kept} in-scope row(s), {dropped} dropped (group filter); "
            f"header: {', '.join(header)}"
        ]
        result = ProbeResult(documents=docs, staged_products=rows, notes=notes)
        if kept == 0:
            result.parameters["staged_zero"] = f"no in-scope rows in the export ({dropped} rows outside the group filter)"
        return result

    def _inspect_register(self, resp, source: SourceRef, docs) -> ProbeResult:
        """The reused register shape-inspect (C1): detect the manufacturer /
        product-ident / nomenclature columns, count the rows, emit the six
        capability findings. Raises UnexpectedFormat on an empty/malformed
        export (the engine degrades to a format finding, run done)."""
        findings, notes = [], []
        method = source.access_method_code or "download"
        ct = resp.headers.get("Content-Type", "").lower()
        text = resp.text
        if "html" in ct or text.lstrip()[:1] == "<":
            # i17: an HTML landing page is not a machine-readable export —
            # record the honest format finding + manual linkage; the actual
            # CSV/API export URL is pinned at the manual capability record.
            findings.append(FindingDraft(metric_code="format", method_code=method,
                                         value_text="HTML landing page — not a CSV/JSON export; export mechanics to confirm"))
            findings.append(FindingDraft(metric_code="cap_cn8_linkage", method_code=method,
                                         value_text="manual"))
            notes.append("HTML landing page; no machine-readable export at this URL — characterize via probe record --mode capability")
            return ProbeResult(documents=docs, findings=findings, notes=notes)
        if "json" in ct or text.lstrip()[:1] in ("{", "["):
            header, data_rows = self._json_register(text, method, findings, notes)
        else:
            header, data_rows = self._csv_register(text, method, findings, notes)
        if header is None:
            return ProbeResult(documents=docs, findings=findings, notes=notes)

        has_manu = any(any(h in c for h in _MANUFACTURER_HINTS) for c in header)
        has_ident = any(any(h in c for h in _PRODUCT_IDENT_HINTS) for c in header)
        has_nomen = any(any(h in c for h in _NOMENCLATURE_HINTS) for c in header)
        n = len(data_rows)

        findings.append(FindingDraft(metric_code="products_identifiable", method_code=method,
                                     value_numeric=n, unit_code="count",
                                     notes=f"export rows: {n}"))
        findings.append(FindingDraft(metric_code="cap_manufacturer", method_code=method,
                                     value_numeric=1 if has_manu else 0))
        findings.append(FindingDraft(metric_code="cap_product_ident", method_code=method,
                                     value_numeric=1 if has_ident else 0))
        if has_nomen:
            linkage, reachable = self._nomenclature_linkage(header, data_rows)
        else:
            linkage, reachable = "manual", 0
            notes.append("no nomenclature column — linkage is manual, CN8 codes deferred to M1")
        findings.append(FindingDraft(metric_code="cap_cn8_linkage", method_code=method,
                                     value_text=linkage))
        findings.append(FindingDraft(metric_code="cap_depth_tier", method_code=method,
                                     value_numeric=self._depth_tier(has_manu, has_ident)))
        findings.append(FindingDraft(metric_code="cn8_reachable", method_code=method,
                                     value_numeric=reachable, unit_code="count",
                                     notes="distinct CN-prefixed codes observed; exact 13-code matching deferred to 0008/M1" if has_nomen else None))
        notes.append(f"shape: manufacturer={has_manu} product_ident={has_ident} nomenclature={has_nomen} rows={n}")
        return ProbeResult(documents=docs, findings=findings, notes=notes)

    @staticmethod
    def _csv_register(text, method, findings, notes):
        # the shared CSV path (e3): BOM/encoding + shape validation live
        # in read_csv_rows; this emits the shape format finding only
        header, data_rows = read_csv_rows(text)
        findings.append(FindingDraft(metric_code="format", method_code=method,
                                     value_text=f"CSV; columns: {', '.join(header)}"))
        return header, data_rows

    @staticmethod
    def _json_register(text, method, findings, notes):
        try:
            data = json.loads(text)
        except ValueError:
            raise UnexpectedFormat("expected JSON but content not parseable",
                                   partial=ProbeResult(documents=[], findings=findings))
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = None
            for key in _JSON_LIST_COUNTS:
                if isinstance(data.get(key), list):
                    items = data[key]
                    break
            if items is None:
                raise UnexpectedFormat("register JSON is not a list payload",
                                       partial=ProbeResult(documents=[], findings=findings))
        else:
            raise UnexpectedFormat("register JSON is not a list payload",
                                   partial=ProbeResult(documents=[], findings=findings))
        if not items:
            raise UnexpectedFormat("empty register export", partial=ProbeResult(documents=[], findings=findings))
        first = items[0]
        if not isinstance(first, dict):
            raise UnexpectedFormat("register JSON rows are not objects",
                                   partial=ProbeResult(documents=[], findings=findings))
        header = [k.strip().lower() for k in first.keys()]
        findings.append(FindingDraft(metric_code="format", method_code=method,
                                     value_text=f"JSON (API); columns: {', '.join(header)}"))
        return header, items

    @staticmethod
    def _nomenclature_linkage(header, data_rows):
        """Mechanism + reachable count for a source with a nomenclature
        column: 'category' taxonomy linkage; count distinct CN codes."""
        nomen_idx = next((i for i, c in enumerate(header) if any(h in c for h in _NOMENCLATURE_HINTS)), None)
        nomen_key = header[nomen_idx] if nomen_idx is not None else None
        codes = set()
        for row in data_rows:
            raw = None
            if nomen_key is not None:
                if isinstance(row, dict):
                    raw = row.get(nomen_key)
                elif nomen_idx < len(row):
                    raw = row[nomen_idx]
            if raw is not None:
                m = _CN_CODE_RE.search(str(raw))
                if m:
                    codes.add(m.group(1))
        return "category", min(len(codes), _CN8_REACHABLE_CAP)

    @staticmethod
    def _depth_tier(has_manu, has_ident):
        """Module-level :func:`depth_tier` (shared with the report — one
        definition, e3/fu8)."""
        return depth_tier(has_manu, has_ident)
