"""Net-marked doctor test (B5): gives `pytest -m net` / `make test-net`
a collectible test; single deterministic request (example.com)."""

import pytest

from leadhs import doctor
from leadhs.cli import Runtime


@pytest.mark.net
def test_doctor_net_reaches_example_com(tmp_path):
    rt = Runtime(db_path=str(tmp_path / "absent.sqlite"), contact="test@example.com")
    result = doctor.run(rt, net=True)
    assert not result.has_errors
    reach = [d for kind, name, d in result.items if name == "reach summary"]
    assert reach and "1/1" in reach[0]
