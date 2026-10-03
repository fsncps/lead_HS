"""Raw source layer (v0.3.0): instruction schema, scanner, seed
interpreter. Submodules: ``instructions`` (schema v1), ``scanner``
(live delivery → draft instruction), ``interpreter`` (init + seed)."""


def delivery_text(resp) -> str:
    """UTF-8-first delivery decode for the raw layer. Live-found rule
    (AS-2, 2026-10-03): ``text/csv`` ships without a charset and
    requests then defaults to ISO-8859-1 — mojibake for every non-ASCII
    value and a BOM artifact in the first header. UTF-8 (BOM-stripped)
    is tried first whenever the declared encoding is a single-byte
    default; a genuinely non-UTF-8 delivery falls back to the requests
    decoding untouched."""
    encoding = (getattr(resp, "encoding", None) or "").lower().replace("-", "").replace("_", "")
    if encoding in ("iso88591", "latin1", "ascii", ""):
        content = resp.content
        if content[:3] == b"\xef\xbb\xbf":
            return content[3:].decode("utf-8")
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            pass
    return resp.text
