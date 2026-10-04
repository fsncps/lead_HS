"""Seed interpreter — instruction-driven bulk acquisition (v0.3.0, r03).

Two phases per instruction: *init* (register-aware source upsert with
the rs6 sync warning, ``raw_source_profile`` upsert with the manifest
hash, create-if-not-exists raw table from the column list) and *seed*
(polite fetches via the single fetch seam, verbatim extraction, upsert
on the natural key + sha256 row hash, ``raw_change`` journal, batch
commits with the checkpoint cursor).

Interpreted at v0.3.0: ``csv_snapshot`` and ``api_endpoint`` with
pagination ``single`` | ``page_param`` | ``offset``. Reserved kinds are
refused with a named message. An interrupt (Ctrl-C) keeps committed
batches + the checkpoint and maps to exit 130; a mid-run failure keeps
both and maps to exit 2; ``raw run --resume`` continues the SAME run
row from the persisted cursor.

Concurrency: ``workers`` page fetches may overlap, but request *starts*
are serialized through a pacer at ``max(delay_seconds, 2.0)`` spacing —
the politeness law holds under any worker count; the DB is written
single-threaded. Values are stored verbatim as TEXT (D44): CSV strings
untouched; JSON scalars JSON-encoded (``true``/``false``/``1.0``),
containers canonical JSON.

Truncation (rs8): when a record exceeds ``payload_budget_bytes`` the
natural-key fields are reserved never truncated, then fields are
truncated worst-priority-first (ties by array order, priority 1 = keep
longest) to fit; UTF-8-safe cuts; ``_truncated`` flags the row; the
row hash is taken AFTER truncation so a truncation change flips it.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional
from urllib.parse import urlencode, urlparse

from .. import db as dbmod
from . import delivery_text
from .instructions import Instruction

BATCH_RECORDS = 500


class InterpreterError(Exception):
    """Named refusal/failure; the CLI maps it to exit 1 (refusal) or 2 (run failure)."""


# --- value + hashing helpers -----------------------------------------


def to_text(value) -> Optional[str]:
    """Verbatim TEXT projection (D44): None stays None; strings pass
    untouched; JSON scalars/containers are JSON-encoded."""
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def _truncate_to_bytes(text: str, max_bytes: int) -> Optional[str]:
    if max_bytes <= 0:
        return None
    cut = text.encode("utf-8")[:max_bytes]
    while cut:
        try:
            return cut.decode("utf-8")
        except UnicodeDecodeError:
            cut = cut[:-1]
    return None


def apply_budget(values: dict, inst: Instruction) -> tuple:
    """Deterministic truncation to the per-record budget; returns
    (values, truncated_flag)."""
    def blen(v) -> int:
        return 0 if v is None else len(v.encode("utf-8"))

    if sum(blen(v) for v in values.values()) <= inst.payload_budget_bytes:
        return values, False
    remaining = inst.payload_budget_bytes - sum(blen(values[k]) for k in inst.natural_key)
    remaining = max(0, remaining)
    out = dict(values)
    # serve priority 1 (keep longest) first; ties by array order —
    # lower priorities absorb the cuts
    order = sorted(
        range(len(inst.columns)),
        key=lambda i: (inst.columns[i].truncation_priority, i),
    )
    for i in order:
        col = inst.columns[i].column
        if col in inst.natural_key:
            continue
        v = out[col]
        if v is None:
            continue
        b = blen(v)
        if b <= remaining:
            remaining -= b
            continue
        out[col] = _truncate_to_bytes(v, remaining)
        remaining = 0
    return out, True


def row_hash(values: dict) -> str:
    """sha256 over the canonical JSON of the (post-truncation) record."""
    payload = json.dumps(values, sort_keys=True, ensure_ascii=False) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def row_key(inst: Instruction, values: dict) -> str:
    if not inst.natural_key:
        return row_hash(values)  # degraded mode: row-hash identity
    return json.dumps([values[k] for k in inst.natural_key], ensure_ascii=False)


# --- extraction -------------------------------------------------------


def extract_csv(text: str, inst: Instruction) -> tuple:
    """Records (dict column→value, verbatim — values untouched, only
    wholly absent cells become None) + ragged-row count."""
    reader = csv.reader(io.StringIO(text), delimiter=inst.delimiter)
    headers = next(reader, None)
    if headers is None:
        raise InterpreterError("delivery has no header row")
    headers = [h.strip() for h in headers]
    records = []
    ragged = 0
    for row in reader:
        if not row or (len(row) == 1 and not row[0].strip()):
            continue
        if len(row) != len(inst.columns):
            ragged += 1
        values = {}
        for i, col in enumerate(inst.columns):
            idx = headers.index(col.source_header) if col.source_header in headers else i
            values[col.column] = row[idx] if idx < len(row) else None
        records.append(values)
    return records, ragged


def _project(rec: dict, path: str):
    """Dot-path projection for nested JSON records ("company.name").
    A plain key is the single-part case; a missing link yields None."""
    cur = rec
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def extract_json(payload, inst: Instruction) -> list:
    if isinstance(payload, list):
        records_raw = payload
    elif isinstance(payload, dict):
        records_raw = None
        for key in ("items", "value", "results", "data", "records"):
            if isinstance(payload.get(key), list):
                records_raw = payload[key]
                break
        if records_raw is None:
            raise InterpreterError("JSON object carries no recognizable record array")
    else:
        raise InterpreterError("JSON payload is neither object nor array")
    records = []
    for rec in records_raw:
        if not isinstance(rec, dict):
            raise InterpreterError("JSON record is not an object")
        records.append({col.column: to_text(_project(rec, col.source_header)) for col in inst.columns})
    return records


def page_url(base: str, inst: Instruction, page: int) -> str:
    if inst.pagination.kind == "single":
        return base
    name = inst.pagination.page_param
    value = page if inst.pagination.kind == "page_param" else (page - 1) * (inst.pagination.page_size or 0)
    sep = "&" if urlparse(base).query else "?"
    return f"{base}{sep}{urlencode({name: value})}"


def page_done(n_records: int, inst: Instruction, page: int) -> bool:
    if inst.pagination.kind == "single":
        return True
    size = inst.pagination.page_size or n_records or 1
    if n_records < size:
        return True
    if inst.pagination.max_pages is not None and page >= inst.pagination.max_pages:
        return True
    return False


# --- pacing (async-safe politeness) ------------------------------------


class Pacer:
    """Serializes request STARTS >= delay apart; workers may overlap
    in-flight requests (the politeness law holds under any worker
    count). The fetch seam's own spacing stays as the safety net."""

    def __init__(self, delay: float, clock: Callable[[], float] = time.monotonic,
                 sleeper: Callable[[float], None] = time.sleep):
        self.delay = max(delay, 2.0)
        self._clock = clock
        self._sleeper = sleeper
        self._next = None
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            now = self._clock()
            if self._next is None:
                self._next = now
            sleep_for = max(0.0, self._next - now)
            self._next = max(now, self._next) + self.delay
        if sleep_for > 0:
            self._sleeper(sleep_for)


# --- init phase --------------------------------------------------------


def resolve_table(conn, inst: Instruction) -> str:
    if inst.table_name:
        return inst.table_name
    from .scanner import resolve_table_name

    return resolve_table_name(conn, inst.source_id)


def ensure_source_row(conn, inst: Instruction) -> list:
    """rs6: register a missing source (warned); never clobber the
    register of record. Returns warning lines."""
    warnings = []
    row = conn.execute("SELECT id, class_code, name FROM source WHERE id = ?", (inst.source_id,)).fetchone()
    access = "api" if inst.export_kind == "api_endpoint" else "download"
    if row is None:
        conn.execute(
            "INSERT INTO source (id, class_code, name, url, access_method_code, verification_status_code, active, notes) "
            "VALUES (?, ?, ?, ?, ?, 'unverified', 1, ?)",
            (inst.source_id, inst.source_class, inst.source_name, inst.list_url, access,
             f"registered by raw run from instruction {inst.manifest_hash()[:16]}…"),
        )
        warnings.append(
            f"{inst.source_id}: not in the register — upserted from the instruction; "
            f"add it to src/leadhs/dict/sources.csv (register of record)"
        )
    else:
        if row["class_code"] != inst.source_class or row["name"] != inst.source_name:
            warnings.append(
                f"{inst.source_id}: instruction metadata differs from the register row "
                f"({row['name']!r}/{row['class_code']}) — register of record wins, nothing changed"
            )
    return warnings


def ensure_profile_row(conn, inst: Instruction, table_name: str) -> None:
    conn.execute(
        """
        INSERT INTO raw_source_profile (source_id, table_name, manifest_hash, export_kind_code,
                                        natural_key_json, payload_budget_bytes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (source_id) DO UPDATE SET
            table_name = excluded.table_name,
            manifest_hash = excluded.manifest_hash,
            export_kind_code = excluded.export_kind_code,
            natural_key_json = excluded.natural_key_json,
            payload_budget_bytes = excluded.payload_budget_bytes
        """,
        (
            inst.source_id, table_name, inst.manifest_hash(), inst.export_kind,
            json.dumps(list(inst.natural_key)), inst.payload_budget_bytes, dbmod.utcnow(),
        ),
    )


def ensure_table(conn, inst: Instruction, table_name: str) -> bool:
    """Create-if-not-exists from the instruction columns + bookkeeping;
    a pinned migration table (0012) already satisfies this. True when
    the table was created now."""
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)
    ).fetchone()
    if exists:
        return False
    cols = ",\n    ".join([f'id INTEGER PRIMARY KEY'] + [f'"{c.column}" TEXT' for c in inst.columns] + [
        '"_row_hash" TEXT NOT NULL',
        '"_first_run_id" INTEGER',
        '"_last_run_id" INTEGER',
        '"_last_changed_run_id" INTEGER',
        '"_truncated" INTEGER NOT NULL DEFAULT 0',
    ])
    conn.execute(f'CREATE TABLE "{table_name}" (\n    {cols}\n)')
    return True


# --- seed phase ---------------------------------------------------------


@dataclass
class SeedStats:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    truncated: int = 0
    ragged: int = 0
    fetches: int = 0
    records: int = 0
    notes: list = field(default_factory=list)


def upsert_record(conn, inst: Instruction, table_name: str, values: dict, run_id: int, stats: SeedStats) -> None:
    values, truncated = apply_budget(values, inst)
    digest = row_hash(values)
    cols = [c.column for c in inst.columns]
    if not inst.natural_key:
        # degraded row-hash identity (data_model): inserts only;
        # byte-identical rows collapse, changed content inserts
        existing = conn.execute(
            f'SELECT id FROM "{table_name}" WHERE "_row_hash" = ?', (digest,)
        ).fetchone()
        if existing is not None:
            stats.skipped += 1
            return
        conn.execute(
            f'INSERT INTO "{table_name}" ({", ".join(chr(34) + c + chr(34) for c in cols)}, '
            f'"_row_hash", "_first_run_id", "_last_run_id", "_truncated") '
            f'VALUES ({", ".join("?" * (len(cols) + 4))})',
            [values[c] for c in cols] + [digest, run_id, run_id, int(truncated)],
        )
        stats.inserted += 1
        if truncated:
            stats.truncated += 1
        return
    key = row_key(inst, values)
    where = " AND ".join(f'"{c}" IS ?' for c in inst.natural_key)
    params = [values[k] for k in inst.natural_key]
    existing = conn.execute(
        f'SELECT id, _row_hash FROM "{table_name}" WHERE {where}', params
    ).fetchone()
    cols = [c.column for c in inst.columns]
    if existing is None:
        conn.execute(
            f'INSERT INTO "{table_name}" ({", ".join(chr(34) + c + chr(34) for c in cols)}, '
            f'"_row_hash", "_first_run_id", "_last_run_id", "_truncated") '
            f'VALUES ({", ".join("?" * (len(cols) + 4))})',
            [values[c] for c in cols] + [digest, run_id, run_id, int(truncated)],
        )
        stats.inserted += 1
    elif existing["id"] is not None and existing["_row_hash"] == digest:
        stats.skipped += 1
        return
    else:
        assignments = ", ".join(f'"{c}" = ?' for c in cols)
        conn.execute(
            f'UPDATE "{table_name}" SET {assignments}, "_row_hash" = ?, "_last_run_id" = ?, '
            f'"_last_changed_run_id" = ?, "_truncated" = ? WHERE id = ?',
            [values[c] for c in cols] + [digest, run_id, run_id, int(truncated), existing["id"]],
        )
        conn.execute(
            "INSERT INTO raw_change (source_id, row_key, old_hash, new_hash, run_id) VALUES (?, ?, ?, ?, ?)",
            (inst.source_id, key, existing["_row_hash"], digest, run_id),
        )
        stats.updated += 1
    if truncated:
        stats.truncated += 1


def _checkpoint_save(conn, run_id: int, state: dict) -> None:
    conn.execute("UPDATE run SET parameters_json = ? WHERE id = ?", (json.dumps(state), run_id))


def _load_cursor(conn, run_id: int) -> dict:
    row = conn.execute("SELECT parameters_json FROM run WHERE id = ?", (run_id,)).fetchone()
    return json.loads(row["parameters_json"] or "{}")


def find_unfinished_run(conn, source_id: str):
    """The newest acquire run with an outstanding cursor (the honest
    'unfinished checkpoint'), or None."""
    rows = conn.execute(
        "SELECT id, run_key, status_code, parameters_json FROM run "
        "WHERE source_id = ? AND kind_code = 'acquire' ORDER BY id DESC LIMIT 5",
        (source_id,),
    ).fetchall()
    for row in rows:
        if row["status_code"] not in ("running", "failed", "aborted"):
            continue
        state = json.loads(row["parameters_json"] or "{}")
        if not state.get("complete") and state.get("cursor"):
            return row
    return None


def seed(conn, fetcher, inst: Instruction, run_id: int, table_name: str,
         cap: Optional[int] = None, workers: int = 1, batch: int = BATCH_RECORDS,
         pacer: Optional[Pacer] = None,
         progress: Optional[Callable[[SeedStats], None]] = None) -> SeedStats:
    """Fetch + extract + upsert with batch checkpoints. Interrupts
    propagate (the caller owns the run-status transitions around it);
    fetch/parse errors raise with committed batches already
    checkpointed."""
    stats = SeedStats()
    state = _load_cursor(conn, run_id)
    state.setdefault("cursor", None)
    state["records"] = state.get("records", 0)

    pacer = pacer or Pacer(inst.politeness.delay_seconds)
    budget = inst.politeness.request_budget_per_run
    total_cap = cap

    def fetch_page(page: int):
        pacer.wait()
        return fetcher.get(page_url(inst.list_url, inst, page))

    def harvest(resp, page: int) -> tuple:
        if inst.export_kind == "csv_snapshot":
            records, ragged = extract_csv(delivery_text(resp), inst)
            stats.ragged += ragged
            return records, True
        payload = json.loads(delivery_text(resp))
        records = extract_json(payload, inst)
        return records, page_done(len(records), inst, page)

    page = 1
    if state["cursor"]:
        page = state["cursor"].get("next", 1)

    while True:
        if stats.fetches >= budget:
            stats.notes.append(
                f"request budget exhausted ({budget} fetches) at record {stats.records} — "
                f"checkpoint kept, raise the budget in the instruction to continue"
            )
            raise BudgetExhausted(stats)
        if total_cap is not None and stats.records >= total_cap:
            break

        batch_pages: list = []
        if inst.pagination.kind in ("page_param", "offset") and workers > 1:
            wanted = min(workers, budget - stats.fetches,
                         (inst.pagination.max_pages - page + 1) if inst.pagination.max_pages else workers)
            pages = list(range(page, page + max(wanted, 1)))
            with ThreadPoolExecutor(max_workers=len(pages)) as pool:
                batch_pages = list(pool.map(fetch_page, pages))
            stats.fetches += len(pages)
        else:
            batch_pages = [fetch_page(page)]
            stats.fetches += 1

        pending = 0
        exhausted = False
        for i, resp in enumerate(batch_pages):
            current = page + i
            records, done = harvest(resp, current)
            for values in records:
                if total_cap is not None and stats.records >= total_cap:
                    break
                upsert_record(conn, inst, table_name, values, run_id, stats)
                stats.records += 1
                pending += 1
                if pending >= batch:
                    state["cursor"] = None if inst.pagination.kind == "single" else {"next": current + 1}
                    state["records"] = stats.records
                    _checkpoint_save(conn, run_id, state)
                    conn.commit()
                    pending = 0
                    if progress:
                        progress(stats)
            if done:
                exhausted = True
                break
            page = current + 1
        if exhausted or inst.pagination.kind == "single":
            break
    # normal loop exit (delivery exhausted or --cap reached): the run is
    # complete; interrupts/failures leave the last committed checkpoint
    state["cursor"] = None
    state["records"] = stats.records
    state["complete"] = True
    _checkpoint_save(conn, run_id, state)
    conn.commit()
    if progress:
        progress(stats)
    return stats


class BudgetExhausted(Exception):
    def __init__(self, stats: SeedStats):
        self.stats = stats
        super().__init__(stats.notes[-1] if stats.notes else "request budget exhausted")


class SeedFailed(Exception):
    def __init__(self, stats: SeedStats, cause: BaseException):
        self.stats = stats
        self.cause = cause
        super().__init__(str(cause))
