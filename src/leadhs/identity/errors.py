"""Canonical identity errors (v0.3.4 r01) — named, one-line remedy in
the message. The CLI maps these to the i1 exit convention: usage/refusal
class → 1, blocked class (drift, backup) → 2.
"""


class IdentityError(Exception):
    """Base — every subclass carries a remedy in its message."""


class SourceMissingError(IdentityError):
    """The raw source table does not exist (never acquired)."""


class SourceSchemaError(IdentityError):
    """A raw table is missing expected columns (layout changed)."""


class ManifestDriftError(IdentityError):
    """The raw table was re-acquired after the last resolve — run
    `leadhs identity rebuild`."""


class NormalizeError(IdentityError):
    """A row/group lacks a normalized key (blank key parts) — skipped
    and counted, never fatal."""


class EmptyNormError(IdentityError):
    """A value normalized to empty or refused (e.g. bad GTIN) — counted."""


class BackupError(IdentityError):
    """The pre-rebuild backup failed — nothing was torn down."""
