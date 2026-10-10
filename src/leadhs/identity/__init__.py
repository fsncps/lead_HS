"""Canonical identity layer (v0.3.4 r01).

Two passes per source: *resolve* derives canonical ``manufacturer`` /
``product`` rows from the verbatim raw tables (group-level identity,
MA12) and back-links every raw row via ``product_uuid``; *rebuild*
backs up, tears down and re-derives everything (il2).

uuid recipe (il4, pinned — changing it means a full rebuild):
``uuid5(NAMESPACE_URL, NAMESPACE + domain + key)`` where NAMESPACE is
``https://github.com/fsncps/lead_HS#identity-v1``, domain is
``manufacturer:`` keyed by the manufacturer name_norm, or
``product:`` keyed by the typed ident_string
(``gtin:<14 digits>`` global | ``article:<mfr_norm>:<ident>`` and
``name:<mfr_norm>:<name_norm>`` manufacturer-scoped).

State machine per source (il2): unresolved → resolved (identity_state
row carries the consumed manifest hash) → drift (raw re-acquired;
resolve refuses, rebuild re-derives) → resolved.
"""

from __future__ import annotations

import uuid

from .adapters import ADAPTERS  # noqa: F401 (registry re-export)
from .errors import (  # noqa: F401
    BackupError,
    EmptyNormError,
    IdentityError,
    ManifestDriftError,
    NormalizeError,
    SourceMissingError,
    SourceSchemaError,
)

NAMESPACE = "https://github.com/fsncps/lead_HS#identity-v1"
DOMAIN_MFR = "manufacturer:"
DOMAIN_PROD = "product:"


def uuid_for(domain: str, key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{NAMESPACE}{domain}{key}"))
