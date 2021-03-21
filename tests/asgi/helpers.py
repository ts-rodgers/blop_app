import dataclasses
from typing import Any, Callable


def transform_item_keys(data: dict, keys):
    for key in keys:
        transform_spec: Any = keys[key] if isinstance(keys, dict) else None

        if "." in key:
            root_key, sub_key = key.split(".", 1)
            root = data[root_key]
            transform_item_keys(root, {sub_key: transform_spec})

        else:
            if not transform_spec:
                transform_spec = {"ops": [{"type": "delete"}]}

            if callable(transform_spec):
                transform_spec = {
                    "ops": [{"type": "replace", "get_value": transform_spec}]
                }

            if isinstance(transform_spec, str):
                transform_spec = {
                    "ops": [{"type": "rename", "new_name": transform_spec}]
                }

            for op in transform_spec["ops"]:
                if op["type"] == "delete":
                    del data[key]
                elif op["type"] == "replace":
                    data[key] = op["get_value"](data[key])
                elif op["type"] == "rename":
                    data[op["new_name"]] = data[key]
                    del data[key]


def get_item_repr(obj: Any, *, strip_keys=None, **transformers):
    data = dataclasses.asdict(obj)
    if strip_keys:
        for key in strip_keys:
            transformers[key] = None

    transform_item_keys(data, transformers)

    return data
