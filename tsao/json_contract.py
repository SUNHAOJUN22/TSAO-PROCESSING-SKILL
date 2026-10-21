"""Strict JSON for decision inputs; duplicate keys cannot overwrite evidence."""

import json

from tsao.numeric_contract import finite


def loads_strict(text: str):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def number(token):
        return finite(token, "JSON numeric value")

    def constant(token):
        raise ValueError(f"non-finite JSON constant: {token}")

    return json.loads(text, object_pairs_hook=pairs, parse_float=number, parse_constant=constant)
