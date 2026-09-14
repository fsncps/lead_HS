"""Identity normalization — shared by ingest and the overlap SQL (fu7).

Exact-match-only (design c5): no fuzzy matching in v0.2.2. The
manufacturer normal form casefolds, folds diacritics, strips legal-form
suffix tokens and collapses punctuation/whitespace; the ident normal
form strips spaces/dashes (leading zeros survive — callers must keep
idents TEXT, e4). The product-name normal form (the ``ident_basis=name``
fallback) folds and collapses whitespace only.
"""

from __future__ import annotations

import re
import unicodedata

_IDENT_TYPES = ("licence", "gtin", "article", "none")

# Trailing tokens removed from a normalized manufacturer (compared against
# the folded text, so punctuation is kept here: "s.a.", "a/s", …). The
# common EU legal forms (design: GmbH, AB, Oy, Ltd, S.A., A/S, …).
_LEGAL_FORM_TOKENS = frozenset(
    {
        "gmbh", "mbh", "ug", "ag", "se", "ev", "kg", "kgaa", "ohg", "partg",
        "gbr", "e.k.", "ek",
        "ab", "hb", "kb", "oy", "oyj", "as", "asa", "a/s", "aps", "ivs",
        "bv", "nv", "vof",
        "ltd", "limited", "plc", "inc", "corp", "corporation", "co",
        "company", "llc", "llp", "lp",
        "sa", "s.a.", "sas", "sasu", "sarl", "s.a.r.l.", "eurl", "scop",
        "srl", "s.r.l.", "spa", "s.p.a.",
        "sro", "s.r.o.", "spol", "a.s.", "doo", "d.o.o.", "dd",
        "kft", "zrt", "uab", "sia", "ou",
    }
)
_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def _fold(text: str) -> str:
    """Diacritic fold + casefold."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.casefold().strip()


def norm_manufacturer(raw) -> str:
    """Manufacturer normal form: fold + casefold, strip legal-form suffix
    tokens (repeatedly), then punctuation → space, whitespace collapse."""
    if raw is None:
        return ""
    text = _fold(str(raw))
    tokens = [t for t in text.split() if t]

    def _is_legal(token: str) -> bool:
        return token in _LEGAL_FORM_TOKENS or token.strip(".,") in _LEGAL_FORM_TOKENS

    while len(tokens) > 1 and _is_legal(tokens[-1]):
        tokens.pop()
    text = _PUNCT_RE.sub(" ", " ".join(tokens))
    return _WS_RE.sub(" ", text).strip()


def norm_ident(raw) -> str:
    """Ident normal form: strip spaces/dashes (incl. NBSP and dash
    variants); case preserved (idents are case-sensitive, e.g. ``DE-1234``)."""
    if raw is None:
        return ""
    text = str(raw)
    for ch in (" ", "\u00a0", "\u2007", "\u202f", "-", "\u2010", "\u2011", "\u2013"):
        text = text.replace(ch, "")
    return text.strip()


def norm_name(raw) -> str:
    """Product-name normal form (``ident_basis=name`` fallback): fold,
    casefold, whitespace collapse — punctuation kept (exact match)."""
    if raw is None:
        return ""
    return _WS_RE.sub(" ", _fold(str(raw))).strip()


def ident_type_of(hint) -> str:
    """Column-hint → ident_type (licence|gtin|article|none)."""
    h = (hint or "").casefold()
    if any(t in h for t in ("licence", "license", "lizenz", "ecat", "nordic", "swan")):
        return "licence"
    if any(t in h for t in ("gtin", "ean", "barcode", "bar_code")):
        return "gtin"
    if any(t in h for t in ("article", "artikel", "sku", "ident", "product_id", "productid", "item")):
        return "article"
    return "none"


def identity(manufacturer_raw, ident_raw, ident_hint, name_raw) -> dict:
    """One normalized identity dict from raw register values — the ingest
    mapping (engine) and the overlap pilot share this exact definition.

    Returns {manufacturer_raw, manufacturer_norm, ident_raw, ident_norm,
    ident_type, ident_basis}: basis ``ident`` when an ident is present,
    else the product-name fallback (``name``) with ident_type ``none``.
    """
    mfr_norm = norm_manufacturer(manufacturer_raw)
    ident_norm = norm_ident(ident_raw)
    if ident_norm:
        ident_type = ident_type_of(ident_hint)
        ident_basis = "ident"
    else:
        ident_type = "none"
        ident_basis = "name"
        ident_norm = norm_name(name_raw)
    return {
        "manufacturer_raw": str(manufacturer_raw) if manufacturer_raw is not None else None,
        "manufacturer_norm": mfr_norm,
        "ident_raw": str(ident_raw) if ident_raw is not None else None,
        "ident_norm": ident_norm,
        "ident_type": ident_type,
        "ident_basis": ident_basis,
    }
