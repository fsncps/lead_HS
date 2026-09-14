"""JSON-stat 2.0 decode — the shared trade-statistics decoder.

Lifted in v0.2.2 (fu10, PHASE01) from the inline one-dimension decoder
built for the v0.2.0 CS-2 aggregation (e2/decision 2A). One tested
implementation serves every Eurostat-API caller: the CS aggregation
(one free dimension) and the per-CN8 × per-declarant Comext batches
(multi-dimension coordinate mapping, W1).

`value` is an object keyed by flat row index, row-major over
``id`` × ``size`` (the Eurostat shape). Errors raise ``JsonstatError``;
callers (adapters) convert to the adapter taxonomy at their boundary.
"""

from __future__ import annotations


class JsonstatError(Exception):
    pass


def category_labels(data: dict, dim: str) -> list:
    """Ordered category labels of one dimension (dict or list index)."""
    cat = data.get("dimension", {}).get(dim, {}).get("category", {})
    index = cat.get("index", {})
    if isinstance(index, dict):
        return [k for k, _ in sorted(index.items(), key=lambda kv: kv[1])]
    return list(index)


def _parts(data: dict):
    """Validated (dim_ids, sizes, value_obj, labels) — one place for the
    shape checks (id/size/value present, label count == declared size)."""
    try:
        dim_ids = data["id"]
        sizes = data["size"]
        value_obj = data["value"]
    except (KeyError, TypeError):
        raise JsonstatError("not a JSON-stat dataset payload (id/size/value missing)")
    if not isinstance(value_obj, dict):
        raise JsonstatError("JSON-stat value is not an object keyed by flat index")
    if not dim_ids or len(dim_ids) != len(sizes):
        raise JsonstatError("JSON-stat id/size dimension mismatch")
    labels = {d: category_labels(data, d) for d in dim_ids}
    for d, s in zip(dim_ids, sizes):
        if len(labels[d]) != s:
            raise JsonstatError(f"dimension {d}: label count != declared size")
    return dim_ids, sizes, value_obj, labels


def decode(data: dict) -> list:
    """Full N-dimension decode: every non-null value as
    ``(labels: {dim: category_label}, value: float)``.

    The flat value index is mapped back through id×size (row-major) to
    per-dimension coordinates, then to category labels — the coordinate
    mapping the per-CN8 × declarant × period batches need (fu10).
    """
    dim_ids, sizes, value_obj, labels = _parts(data)
    rows = []
    for key, raw in value_obj.items():
        try:
            flat = int(key)
        except (TypeError, ValueError):
            continue
        if raw is None:
            continue
        rest = flat
        coords = []
        for s in reversed(sizes):
            coords.append(rest % s)
            rest //= s
        coords.reverse()
        rows.append(({d: labels[d][c] for d, c in zip(dim_ids, coords)}, float(raw)))
    return rows


def one_dim(data: dict) -> list:
    """One-free-dimension convenience (the CS aggregation shape): the
    only dimension with size > 1 carries the values; returns
    ``[(category_label, value)]``. More than one free dimension is an
    error — use :func:`decode` and pick dimensions explicitly."""
    dim_ids, sizes, _, _ = _parts(data)
    free = [(i, d) for i, (d, s) in enumerate(zip(dim_ids, sizes)) if s > 1]
    if len(free) != 1:
        raise JsonstatError(
            f"decoder supports exactly one free dimension, got {[d for _, d in free]}"
        )
    free_dim = free[0][1]
    rows = decode(data)
    return [(labels[free_dim], v) for labels, v in rows]


def sum_pairs(pairs: list) -> tuple:
    """(total, top-5) of ``(label, value)`` pairs — the aggregation sum."""
    total = sum(v for _, v in pairs)
    tops = sorted(pairs, key=lambda kv: kv[1], reverse=True)[:5]
    return total, tops
