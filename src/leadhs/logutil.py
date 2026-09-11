"""Shared structured logging helper (A2).

Single ``log_event()`` — every module logs through it, never bare
print / hand-rolled formats. One line: module, event, then the
caller's fields (url, status, ms, source, run ...) in insertion
order, timestamps added by the CLI's logging formatter.
"""

from __future__ import annotations

import logging

__all__ = ["log_event", "configure_logging"]


def log_event(logger: logging.Logger, module: str, event: str, **fields) -> None:
    parts = [module, event]
    for key, value in fields.items():
        if value is not None:
            parts.append(f"{key}={value}")
    logger.info(" ".join(parts))


def configure_logging(verbose: bool) -> logging.Logger:
    """Root logger with a UTC-timestamped formatter; no-op-ish quiet mode."""
    logger = logging.getLogger("leadhs")
    if verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"))
    handler.formatter.converter = _utc
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def _utc(*args) -> "time.struct_time":
    import time

    return time.gmtime(*args)