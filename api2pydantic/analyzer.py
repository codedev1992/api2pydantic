"""
Analyze JSON data and infer types, patterns, and constraints.
"""

import json
import re
from typing import Any, Dict, List, Set, Union, Optional
from datetime import datetime
from uuid import UUID
from collections import defaultdict


class FieldInfo:
    """Information about a field in the JSON structure."""

    def __init__(self, name: str):
        self.name = name
        self.types: Set[str] = set()
        self.is_nullable = False
        self.examples: List[Any] = []
        self.min_value: Optional[float] = None
        self.max_value: Optional[float] = None
        self.min_length: Optional[int] = None
        self.max_length: Optional[int] = None
        self.pattern: Optional[str] = None
        self.enum_values: Set[Any] = set()
        self.nested_schema: Optional[Dict] = None
        self.array_item_schema: Optional[Dict] = None


def analyze_json(json_data: Union[str, dict, list]) -> Dict:
    """
    Analyze JSON data and infer schema information.

    Args:
        json_data: JSON string, dict, or list

    Returns:
        Schema dictionary with type information
    """
    # Parse JSON if string
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Analyze the structure
    return _analyze_value(data, "root")


def _analyze_value(value: Any, field_name: str = "root") -> Dict:
    """Recursively analyze a value and determine its type and constraints."""

    field_info = FieldInfo(field_name)

    if value is None:
        field_info.is_nullable = True
        field_info.types.add("None")
    elif isinstance(value, bool):
        field_info.types.add("bool")
        field_info.examples.append(value)
    elif isinstance(value, int):
        field_info.types.add("int")
        field_info.examples.append(value)
        _update_numeric_constraints(field_info, value)
    elif isinstance(value, float):
        field_info.types.add("float")
        field_info.examples.append(value)
        _update_numeric_constraints(field_info, value)
    elif isinstance(value, str):
        _analyze_string(field_info, value)
    elif isinstance(value, list):
        _analyze_list(field_info, value)
    elif isinstance(value, dict):
        _analyze_dict(field_info, value)

    return _field_info_to_dict(field_info)


def _analyze_string(field_info: FieldInfo, value: str) -> None:
    """Analyze string value and detect special types."""

    field_info.examples.append(value)

    # Update length constraints
    length = len(value)
    if field_info.min_length is None or length < field_info.min_length:
        field_info.min_length = length
    if field_info.max_length is None or length > field_info.max_length:
        field_info.max_length = length

    # Try to detect special string types
    detected_type = _detect_string_type(value)
    field_info.types.add(detected_type)

    # Collect for potential enum detection (limit to 20 unique values)
    if len(field_info.enum_values) < 20:
        field_info.enum_values.add(value)


def _detect_string_type(value: str) -> str:
    """Detect special string types (UUID, datetime, email, URL, etc.)."""

    # UUID detection
    if _is_uuid(value):
        return "UUID"

    # Datetime detection
    if _is_datetime(value):
        return "datetime"

    # Date detection
    if _is_date(value):
        return "date"

    # Email detection
    if _is_email(value):
        return "EmailStr"

    # URL detection
    if _is_url(value):
        return "HttpUrl"

    return "str"


def _is_uuid(value: str) -> bool:
    """Check if string is a valid UUID."""
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def _is_datetime(value: str) -> bool:
    """Check if string is a valid datetime."""
    datetime_patterns = [
        r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",
        r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d+",
        r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}",
        r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}Z",
    ]

    for pattern in datetime_patterns:
        if re.match(pattern, value):
            return True

    return False


def _is_date(value: str) -> bool:
    """Check if string is a valid date."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value))


def _is_email(value: str) -> bool:
    """Check if string is a valid email."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, value))


def _is_url(value: str) -> bool:
    """Check if string is a valid URL."""
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(url_pattern, value, re.IGNORECASE))


def _analyze_list(field_info: FieldInfo, values: list) -> None:
    """Analyze list and determine item types."""

    field_info.types.add("List")

    if not values:
        # Empty list - default to List[Any]
        field_info.array_item_schema = {"types": ["Any"], "is_nullable": False}
        return

    # Analyze all items to determine common type
    item_schemas = []
    for item in values[:100]:  # Analyze up to 100 items for better inference
        item_schema = _analyze_value(item, "item")
        item_schemas.append(item_schema)

    # Merge item schemas to find common type
    field_info.array_item_schema = _merge_schemas(item_schemas)


def _analyze_dict(field_info: FieldInfo, obj: dict) -> None:
    """Analyze dictionary and create nested schema."""

    field_info.types.add("Dict")

    if not obj:
        field_info.nested_schema = {}
        return

    # Analyze each field in the dictionary
    nested_fields = {}
    for key, value in obj.items():
        nested_fields[key] = _analyze_value(value, key)

    field_info.nested_schema = nested_fields


def _merge_schemas(schemas: List[Dict]) -> Dict:
    """Merge multiple schemas to find common type."""

    if not schemas:
        return {"types": ["Any"], "is_nullable": False}

    # Collect all types from schemas
    all_types = set()
    is_nullable = False
    nested_schemas = []
    all_examples = []

    for schema in schemas:
        types = schema.get("types", [])
        all_types.update(types)
        if schema.get("is_nullable"):
            is_nullable = True
        if schema.get("nested_schema"):
            nested_schemas.append(schema["nested_schema"])
        if schema.get("examples"):
            all_examples.extend(schema.get("examples", [])[:1])  # Keep first example from each

    # Remove None from types
    all_types.discard("None")

    # If only one type, use it
    if len(all_types) == 1:
        merged_type = list(all_types)[0]
        result = {"types": [merged_type], "is_nullable": is_nullable}

        # If it's a nested dict, merge nested schemas
        if merged_type == "Dict" and nested_schemas:
            result["nested_schema"] = _merge_nested_schemas(nested_schemas)

        # Add examples
        if all_examples:
            result["examples"] = all_examples[:3]

        return result

    # Multiple types - return as list
    result = {"types": list(all_types), "is_nullable": is_nullable}

    if all_examples:
        result["examples"] = all_examples[:3]

    return result


def _merge_nested_schemas(nested_schemas: List[Dict]) -> Dict:
    """Merge multiple nested object schemas."""

    # Collect all fields across all schemas
    all_fields = defaultdict(list)

    for schema in nested_schemas:
        for field_name, field_schema in schema.items():
            all_fields[field_name].append(field_schema)

    # Merge each field
    merged = {}
    for field_name, field_schemas in all_fields.items():
        merged[field_name] = _merge_schemas(field_schemas)
        # Field is nullable if it doesn't appear in all schemas
        if len(field_schemas) < len(nested_schemas):
            merged[field_name]["is_nullable"] = True

    return merged


def _update_numeric_constraints(field_info: FieldInfo, value: Union[int, float]) -> None:
    """Update numeric min/max constraints."""

    if field_info.min_value is None or value < field_info.min_value:
        field_info.min_value = value
    if field_info.max_value is None or value > field_info.max_value:
        field_info.max_value = value


def _field_info_to_dict(field_info: FieldInfo) -> Dict:
    """Convert FieldInfo object to dictionary."""

    result = {
        "name": field_info.name,
        "types": list(field_info.types),
        "is_nullable": field_info.is_nullable,
    }

    if field_info.examples:
        result["examples"] = field_info.examples[:3]  # Keep first 3 examples

    if field_info.min_value is not None:
        result["min_value"] = field_info.min_value
    if field_info.max_value is not None:
        result["max_value"] = field_info.max_value

    if field_info.min_length is not None:
        result["min_length"] = field_info.min_length
    if field_info.max_length is not None:
        result["max_length"] = field_info.max_length

    # Enum detection - if we have 2-10 unique values, it might be an enum
    if 2 <= len(field_info.enum_values) <= 10:
        result["enum_values"] = list(field_info.enum_values)

    if field_info.nested_schema is not None:
        result["nested_schema"] = field_info.nested_schema

    if field_info.array_item_schema is not None:
        result["array_item_schema"] = field_info.array_item_schema

    return result
