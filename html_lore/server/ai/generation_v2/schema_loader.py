from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

from .schemas import TextEnum


T = TypeVar("T")


class AgentOutputSchemaError(ValueError):
    pass


def parse_dataclass_json(raw: str, cls: type[T]) -> T:
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentOutputSchemaError(f"Invalid JSON: {exc.msg}") from exc
    if not isinstance(decoded, dict):
        raise AgentOutputSchemaError("Agent output must be a JSON object.")
    return dataclass_from_dict(decoded, cls)


def dataclass_from_dict(data: dict[str, Any], cls: type[T]) -> T:
    if not is_dataclass(cls):
        raise AgentOutputSchemaError(f"Unsupported schema type: {cls!r}")
    values: dict[str, Any] = {}
    type_hints = get_type_hints(cls)
    for field in fields(cls):
        if field.name not in data:
            continue
        values[field.name] = coerce_value(data[field.name], type_hints.get(field.name, field.type))
    try:
        return cls(**values)
    except TypeError as exc:
        raise AgentOutputSchemaError(str(exc)) from exc


def coerce_value(value: Any, annotation: Any) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is list:
        item_type = args[0] if args else Any
        if not isinstance(value, list):
            raise AgentOutputSchemaError("Expected a list field.")
        return [coerce_value(item, item_type) for item in value]
    if origin is dict:
        if not isinstance(value, dict):
            raise AgentOutputSchemaError("Expected a dict field.")
        return value
    if is_dataclass(annotation):
        if not isinstance(value, dict):
            raise AgentOutputSchemaError("Expected an object field.")
        return dataclass_from_dict(value, annotation)
    if isinstance(annotation, type) and issubclass(annotation, TextEnum):
        try:
            return annotation(value)
        except ValueError as exc:
            raise AgentOutputSchemaError(f"Invalid enum value: {value}") from exc
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        try:
            return annotation(value)
        except ValueError as exc:
            raise AgentOutputSchemaError(f"Invalid enum value: {value}") from exc
    return value
