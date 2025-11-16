"""
Utility functions for api2pydantic.
"""

import re
from typing import Any, Dict


def sanitize_field_name(name: str) -> str:
    """
    Sanitize field name to be a valid Python identifier.

    Args:
        name: Original field name

    Returns:
        Valid Python identifier
    """
    # Replace invalid characters with underscore
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)

    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"field_{sanitized}"

    # Handle Python keywords
    if sanitized in PYTHON_KEYWORDS:
        sanitized = f"{sanitized}_"

    return sanitized or "field"


def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    # Insert underscore before uppercase letters
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # Insert underscore before uppercase letters preceded by lowercase
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    # Split on non-alphanumeric characters
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(part.capitalize() for part in parts if part)


def format_code(code: str) -> str:
    """
    Basic code formatting (remove extra blank lines, etc.).

    Args:
        code: Python code string

    Returns:
        Formatted code
    """
    lines = code.split("\n")

    formatted_lines = []
    prev_blank = False

    for line in lines:
        is_blank = not line.strip()

        if is_blank:
            if not prev_blank:
                formatted_lines.append(line)
            prev_blank = True
        else:
            formatted_lines.append(line)
            prev_blank = False

    return "\n".join(formatted_lines)


def merge_schemas(schema1: Dict, schema2: Dict) -> Dict:
    """
    Merge two schemas to create a more comprehensive type definition.

    Args:
        schema1: First schema
        schema2: Second schema

    Returns:
        Merged schema
    """
    # This is a simplified merge - in practice you'd want more sophisticated logic
    merged = schema1.copy()

    # Merge types
    if "types" in schema2:
        types1 = set(merged.get("types", []))
        types2 = set(schema2["types"])
        merged["types"] = list(types1 | types2)

    # Update nullable flag
    if schema2.get("is_nullable"):
        merged["is_nullable"] = True

    return merged


# Python reserved keywords
PYTHON_KEYWORDS = {
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
}
