"""Adapter registry — v0.2.3 PHASE02 split (TODOS watch item).

One adapter class per module (``cs.py``, ``pe.py``, ``as.py``,
``st.py``) with the shared helpers in ``_common.py``; the public
import surface is unchanged — every name the engine, the tests and
prior units import keeps living here (``leadhs.probe.adapters``).
Registration runs on package import, same as the pre-split monolith.
"""

from ...fetch import SizeLimit  # noqa: F401  (re-exported pre-split)
from ._common import (  # noqa: F401
    AdapterError,
    BinaryMissing,
    ExtractionError,
    ParseError,
    ProbeAdapter,
    UnexpectedFormat,
    get_adapter,
    registry,
)
from .cs import CSAdapter  # noqa: F401
from .pe import PEAdapter  # noqa: F401
from .st import STAdapter  # noqa: F401
from .as_adapter import ASAdapter  # noqa: F401
from . import _common  # noqa: F401

# Dispatch order preserved from the pre-split monolith (CS, PE, ST, AS).
register_calls = [CSAdapter, PEAdapter, STAdapter, ASAdapter]
for _cls in register_calls:
    _common.register(_cls())

__all__ = [
    "AdapterError",
    "UnexpectedFormat",
    "BinaryMissing",
    "ExtractionError",
    "ParseError",
    "SizeLimit",
    "ProbeAdapter",
    "registry",
    "get_adapter",
    "register",
    "CSAdapter",
    "PEAdapter",
    "STAdapter",
    "ASAdapter",
    "read_csv_rows",
    "sniff_kind",
    "depth_tier",
]


def register(adapter):
    """Module-level alias (pre-split surface) → the shared registry."""
    return _common.register(adapter)


def _log(ctx, event, **fields):  # noqa: F401  (pre-split surface)
    return _common._log(ctx, event, **fields)


def sniff_kind(content_type, head):  # noqa: F401  (pre-split surface)
    return _common.sniff_kind(content_type, head)


def read_csv_rows(text, *, separator=",", expected=None):  # noqa: F401
    return _common.read_csv_rows(text, separator=separator, expected=expected)


def depth_tier(has_manu, has_ident):  # noqa: F401  (pre-split surface)
    return _common.depth_tier(has_manu, has_ident)
