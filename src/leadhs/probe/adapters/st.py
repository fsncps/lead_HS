"""ST adapter — SPIN download + extraction check (mdbtools).

v0.2.3 PHASE02 split (TODOS watch item): one adapter class per module;
the shared helpers live in ``_common.py``; the public import surface
stays ``leadhs.probe.adapters`` (package __init__ re-exports).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from urllib.parse import urljoin

from ...fetch import Blocked
from ...models import FindingDraft, ProbeResult, SourceRef
from ._common import BinaryMissing, ExtractionError, _doc, _log, _match_link, _soup

# --- ST adapter (SPIN download + extraction check) -------------------------


_ST_DOWNLOAD_HINTS = ("page_id=54", ".mdb", ".zip", "access", "download", "datenbank")
_MDB_BINARIES = ("mdb-export", "mdb-tables")


class STAdapter:
    key = "ST"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "ST"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
        if ctx.dry_run:
            ctx.fetcher.plan(source.url)
            return ProbeResult()
        base = source.url
        resp = ctx.fetcher.get(base)
        _log(ctx, "st_get", url=base, status=resp.status_code)
        docs = [_doc(base, resp, retrieval_method_code="download")]
        findings = [
            FindingDraft(metric_code="robots", method_code="download", value_text=ctx.fetcher.robots_policy(base)),
            FindingDraft(metric_code="format", method_code="download", value_text="web site + free Access-DB download"),
            FindingDraft(metric_code="free_access", method_code="download", value_numeric=1),
        ]
        notes = []

        soup = _soup(resp)
        db_link = _match_link(soup, _ST_DOWNLOAD_HINTS)
        if not db_link:
            findings.append(FindingDraft(metric_code="extraction_path", method_code="manual", value_text="no Access-DB download link found on landing page"))
            notes.append("download link not found on landing page")
            return ProbeResult(documents=docs, findings=findings, notes=notes)

        dl_url = urljoin(base, db_link)
        try:
            dl_resp = ctx.fetcher.get(dl_url)
        except Blocked as exc:
            raise Blocked(dl_url, f"download blocked: {exc.detail}")
        _log(ctx, "st_download", url=dl_url, status=dl_resp.status_code, bytes=len(dl_resp.content))
        ext = "mdb" if ".mdb" in dl_url.lower() else ("zip" if ".zip" in dl_url.lower() else "bin")
        docs.append(_doc(dl_url, dl_resp, retrieval_method_code="download"))

        binary = next((b for b in _MDB_BINARIES if shutil.which(b)), None)
        if binary is None:
            raise BinaryMissing(
                "mdbtools not on PATH (mdb-export/mdb-tables absent)",
                partial=ProbeResult(documents=docs, findings=findings),
                url=base,
            )

        with tempfile.NamedTemporaryFile(suffix=".mdb", delete=False) as tmp:
            tmp.write(dl_resp.content)
            tmp_path = tmp.name
        try:
            out = subprocess.run([binary, "-1", tmp_path], capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            raise ExtractionError("mdb extraction timed out", partial=ProbeResult(documents=docs, findings=findings), url=base)
        except OSError as exc:
            raise BinaryMissing(f"mdbtools failed to run: {exc}", partial=ProbeResult(documents=docs, findings=findings), url=base)
        finally:
            os.unlink(tmp_path)
        if out.returncode != 0:
            raise ExtractionError(
                f"{binary} exit {out.returncode}: {out.stderr.decode(errors='replace')[:200]}",
                partial=ProbeResult(documents=docs, findings=findings),
                url=base,
            )
        tables = out.stdout.decode(errors="replace").splitlines()
        findings.append(FindingDraft(metric_code="extraction_path", method_code="download", value_text=f"mdbtools ok ({binary}); tables: {', '.join(tables[:10])}"))
        notes.append(f"extracted {len(tables)} tables")
        return ProbeResult(documents=docs, findings=findings, notes=notes)
