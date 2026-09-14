"""JSON-stat module (v0.2.2 fu10): one-dim decode (ported v0.2.0 e2/2A
fixtures) + multi-dimension coordinate mapping for the per-CN8
Comext batches."""

import pytest

from leadhs.jsonstat import JsonstatError, category_labels, decode, one_dim, sum_pairs


def _one_dim_payload(values: dict, labels=None) -> dict:
    """The v0.2.0 e2/2A shape: partner as the one free dimension; value
    object keyed by flat index. ``labels`` keeps the full dimension
    shape when the result set is empty."""
    keys = labels or list(values)
    index = {k: i for i, k in enumerate(keys)}
    return {
        "version": "2.0",
        "class": "dataset",
        "id": ["partner"],
        "size": [len(keys)],
        "dimension": {"partner": {"category": {"index": index, "label": {}}}},
        "value": {str(i): v for i, v in enumerate(values.values())},
    }


def _two_dim_payload() -> dict:
    """W1 batch shape: declarant × period free, flow + cn8 pinned at
    size 1 — value object keyed by flat index over id×size row-major."""
    index = {
        "declarant": {"DE": 0, "FR": 1},
        "period": {"2023": 0, "2024": 1},
        "flow": {"1": 0},
        "cn8": {"32081000": 0},
    }
    return {
        "version": "2.0",
        "class": "dataset",
        "id": ["declarant", "period", "flow", "cn8"],
        "size": [2, 2, 1, 1],
        "dimension": {d: {"category": {"index": index[d], "label": {}}} for d in index},
        "value": {"0": 100.0, "1": 120.0, "2": 30.0, "3": 45.0},
    }


# --- one-dimension decode (ported fixtures) --------------------------------


def test_one_dim_decodes_partner_values():
    assert one_dim(_one_dim_payload({"DE": 100.0, "FR": 250.0, "BE": 50.0})) == [
        ("DE", 100.0),
        ("FR", 250.0),
        ("BE", 50.0),
    ]


def test_one_dim_empty_value_object():
    assert one_dim(_one_dim_payload({}, labels=["DE", "FR", "IT"])) == []


def test_one_dim_skips_nulls_and_bad_keys():
    payload = _one_dim_payload({"DE": 1.0, "FR": 2.0, "BE": 3.0})
    payload["value"] = {"0": 1.0, "1": None, "x": 9.9, "2": 3.0}
    assert one_dim(payload) == [("DE", 1.0), ("BE", 3.0)]


def test_one_dim_rejects_two_free_dims():
    payload = _one_dim_payload({"DE": 1.0, "FR": 2.0})
    payload["id"] = ["partner", "flow"]
    payload["size"] = [2, 2]
    payload["dimension"]["flow"] = {"category": {"index": {"1": 0, "2": 1}, "label": {}}}
    with pytest.raises(JsonstatError) as exc:
        one_dim(payload)
    assert "exactly one free dimension" in str(exc.value)


def test_shape_errors():
    with pytest.raises(JsonstatError) as exc:
        one_dim({"value": {}})
    assert "id/size/value" in str(exc.value)
    with pytest.raises(JsonstatError) as exc:
        one_dim(_one_dim_payload({"DE": 1.0}) | {"value": "not-a-dict"})
    assert "not an object" in str(exc.value)
    payload = _one_dim_payload({"DE": 1.0, "FR": 2.0})
    payload["size"] = [3]
    with pytest.raises(JsonstatError) as exc:
        one_dim(payload)
    assert "label count != declared size" in str(exc.value)


# --- multi-dimension decode (W1 batch shape) --------------------------------


def test_decode_maps_every_dimension():
    rows = decode(_two_dim_payload())
    assert dict(rows[0][0]) == {
        "declarant": "DE",
        "period": "2023",
        "flow": "1",
        "cn8": "32081000",
    }
    assert [v for _, v in rows] == [100.0, 120.0, 30.0, 45.0]


def test_decode_flat_index_row_major():
    rows = decode(_two_dim_payload())
    by_coord = {(l["declarant"], l["period"]): v for l, v in rows}
    # flat 0 = (DE, 2023), flat 1 = (DE, 2024), flat 2 = (FR, 2023), flat 3 = (FR, 2024)
    assert by_coord == {("DE", "2023"): 100.0, ("DE", "2024"): 120.0,
                        ("FR", "2023"): 30.0, ("FR", "2024"): 45.0}


def test_decode_skips_nulls():
    payload = _two_dim_payload()
    payload["value"] = {"0": 100.0, "1": None}
    rows = decode(payload)
    assert len(rows) == 1 and rows[0][0]["period"] == "2023"


# --- helpers -----------------------------------------------------------------


def test_category_labels_dict_and_list_index():
    payload = _one_dim_payload({"DE": 1.0})
    assert category_labels(payload, "partner") == ["DE"]
    payload["dimension"]["partner"]["category"]["index"] = ["B", "A"]
    assert category_labels(payload, "partner") == ["B", "A"]


def test_sum_pairs_total_and_tops():
    total, tops = sum_pairs([("DE", 250.0), ("FR", 100.0), ("BE", 50.0), ("IT", 1.0)])
    assert total == 401.0
    assert tops[:2] == [("DE", 250.0), ("FR", 100.0)]
