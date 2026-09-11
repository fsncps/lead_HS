"""Probe report rendering from the views (md default; csv/json).

P7: every user-facing count comes from the DB only. Anchor candidates
are listed as provisional — promotion is a manual M1 method decision,
never automatic (D20).
"""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

from jinja2 import Environment, PackageLoader

_TEMPLATE = "probe_report.md.j2"


def _fetch_census(conn, source_id: Optional[str] = None) -> list:
    if source_id:
        rows = conn.execute(
            "SELECT source_id, metric_code, value_numeric, value_text, unit_code, method_code, run_key, started_at "
            "FROM v_probe_latest WHERE source_id = ? ORDER BY source_id, metric_code",
            (source_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT source_id, metric_code, value_numeric, value_text, unit_code, method_code, run_key, started_at "
            "FROM v_probe_latest ORDER BY source_id, metric_code"
        ).fetchall()
    return [dict(r) for r in rows]


def _fetch_anchors(conn, source_id: Optional[str] = None) -> list:
    if source_id:
        rows = conn.execute(
            "SELECT source_id, metric_code, value_numeric, unit_code, run_key FROM v_anchor_candidates WHERE source_id = ? "
            "ORDER BY source_id, metric_code",
            (source_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT source_id, metric_code, value_numeric, unit_code, run_key FROM v_anchor_candidates "
            "ORDER BY source_id, metric_code"
        ).fetchall()
    return [dict(r) for r in rows]


def _fetch_activity(conn) -> list:
    rows = conn.execute(
        "SELECT source_id, first_retrieved_at, last_retrieved_at, run_count, finding_count FROM v_source_activity ORDER BY source_id"
    ).fetchall()
    return [dict(r) for r in rows]


def _fmt_value(row: dict) -> str:
    if row["value_numeric"] is not None:
        v = str(row["value_numeric"])
        return v + (f" {row['unit_code']}" if row["unit_code"] else "")
    return row["value_text"] or ""


def _by_source(rows: list) -> dict:
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row)
    return grouped


def render(conn, format: str = "md", source_id: Optional[str] = None) -> str:
    census = _fetch_census(conn, source_id)
    anchors = _fetch_anchors(conn, source_id)
    activity = _fetch_activity(conn)
    if format == "md":
        env = Environment(loader=PackageLoader("leadhs", "templates"))
        return env.get_template(_TEMPLATE).render(
            census=_by_source(census), anchors=anchors, activity=activity,
            fmt=_fmt_value, source_filter=source_id,
        )
    if format == "csv":
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["source_id", "metric_code", "value", "unit_code", "method_code", "run_key", "started_at"])
        for row in census:
            writer.writerow([row["source_id"], row["metric_code"], _fmt_value(row), row["unit_code"], row["method_code"], row["run_key"], row["started_at"]])
        return out.getvalue()
    if format == "json":
        return json.dumps({"census": census, "anchor_candidates": anchors, "source_activity": activity}, indent=2)
    raise ValueError(f"unknown format {format!r}")