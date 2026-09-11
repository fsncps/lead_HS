"""logutil: single helper, one structured line (A2)."""

import logging


def test_log_event_single_line():
    logger = logging.getLogger("leadhs.test")
    logger.setLevel(logging.INFO)
    records = []
    handler = logging.Handler()
    handler.emit = lambda record: records.append(record.getMessage())
    logger.addHandler(handler)
    from leadhs.logutil import log_event

    log_event(logger, "engine", "run_done", source="CS-1", status="done", ms=123, url=None)
    assert len(records) == 1
    line = records[0]
    assert line.startswith("engine run_done")
    assert "source=CS-1" in line
    assert "status=done" in line
    assert "ms=123" in line
    assert "url=" not in line  # None fields are dropped
