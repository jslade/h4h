

from typing import Any


def deep_dict(data: dict[str, Any]) -> dict:
    return { k: _deep_dict(v) for k, v in data.items()}

def _deep_dict(v: Any) -> Any:
    t = type(v)
    if t is dict:
        return deep_dict(v)
    if t is list:
        return [_deep_dict(v_) for v_ in v]
    if t is int or t is float or t is str or t is bool:
        return v
    return str(v)
     