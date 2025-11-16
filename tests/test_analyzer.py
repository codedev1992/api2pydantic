"""
Tests for the analyzer module.
"""

import pytest
from api2pydantic.analyzer import (
    analyze_json,
    _detect_string_type,
    _is_uuid,
    _is_datetime,
    _is_email,
    _is_url,
)


def test_analyze_simple_object():
    """Test analyzing a simple JSON object."""
    json_data = {"name": "John Doe", "age": 30, "is_active": True}

    schema = analyze_json(json_data)

    assert "nested_schema" in schema
    assert "name" in schema["nested_schema"]
    assert "age" in schema["nested_schema"]
    assert "is_active" in schema["nested_schema"]


def test_analyze_nested_object():
    """Test analyzing nested JSON objects."""
    json_data = {"user": {"name": "John", "profile": {"bio": "Developer"}}}

    schema = analyze_json(json_data)

    assert "nested_schema" in schema
    assert "user" in schema["nested_schema"]
    user_schema = schema["nested_schema"]["user"]
    assert "nested_schema" in user_schema


def test_analyze_array():
    """Test analyzing arrays."""
    json_data = {"tags": ["python", "pydantic", "api"]}

    schema = analyze_json(json_data)

    assert "nested_schema" in schema
    assert "tags" in schema["nested_schema"]
    tags_schema = schema["nested_schema"]["tags"]
    assert "List" in tags_schema["types"]
    assert "array_item_schema" in tags_schema


def test_detect_uuid():
    """Test UUID detection."""
    assert _is_uuid("123e4567-e89b-12d3-a456-426614174000")
    assert not _is_uuid("not-a-uuid")


def test_detect_datetime():
    """Test datetime detection."""
    assert _is_datetime("2024-01-15T10:30:00Z")
    assert _is_datetime("2024-01-15T10:30:00.123456Z")
    assert _is_datetime("2024-01-15 10:30:00")
    assert not _is_datetime("not-a-datetime")


def test_detect_email():
    """Test email detection."""
    assert _is_email("user@example.com")
    assert _is_email("test.user+tag@example.co.uk")
    assert not _is_email("not-an-email")


def test_detect_url():
    """Test URL detection."""
    assert _is_url("https://example.com")
    assert _is_url("http://example.com/path")
    assert not _is_url("not-a-url")


def test_string_type_detection():
    """Test overall string type detection."""
    assert _detect_string_type("123e4567-e89b-12d3-a456-426614174000") == "UUID"
    assert _detect_string_type("2024-01-15T10:30:00Z") == "datetime"
    assert _detect_string_type("user@example.com") == "EmailStr"
    assert _detect_string_type("https://example.com") == "HttpUrl"
    assert _detect_string_type("regular string") == "str"


def test_nullable_fields():
    """Test detection of nullable fields."""
    json_data = {"optional_field": None, "required_field": "value"}

    schema = analyze_json(json_data)

    assert schema["nested_schema"]["optional_field"]["is_nullable"]
    assert not schema["nested_schema"]["required_field"].get("is_nullable", False)


def test_numeric_constraints():
    """Test numeric constraint detection."""
    json_data = {"age": 30, "score": 95.5}

    schema = analyze_json(json_data)

    age_schema = schema["nested_schema"]["age"]
    assert "int" in age_schema["types"]
    assert "min_value" in age_schema
    assert "max_value" in age_schema


def test_string_length_constraints():
    """Test string length constraint detection."""
    json_data = {"short": "hi", "long": "this is a longer string"}

    schema = analyze_json(json_data)

    short_schema = schema["nested_schema"]["short"]
    assert "min_length" in short_schema
    assert short_schema["min_length"] == 2


def test_empty_array():
    """Test handling of empty arrays."""
    json_data = {"empty": []}

    schema = analyze_json(json_data)

    empty_schema = schema["nested_schema"]["empty"]
    assert "List" in empty_schema["types"]


def test_mixed_type_array():
    """Test handling of arrays with mixed types."""
    json_data = {"mixed": [1, "string", True]}

    schema = analyze_json(json_data)

    mixed_schema = schema["nested_schema"]["mixed"]
    assert "List" in mixed_schema["types"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
