"""
Generate Pydantic model code from analyzed schema.
"""

from typing import Dict, List, Set, Optional


class PydanticModelGenerator:
    """Generator for Pydantic model code."""

    def __init__(
        self,
        include_validators: bool = True,
        include_descriptions: bool = True,
        force_optional: bool = False,
    ):
        self.include_validators = include_validators
        self.include_descriptions = include_descriptions
        self.force_optional = force_optional
        self.imports: Set[str] = set()
        self.nested_models: List[str] = []
        self.indent_level = 0

    def generate(self, schema: Dict, model_name: str = "RootModel") -> str:
        """Generate complete Pydantic model code."""

        self.imports = {"from pydantic import BaseModel, Field"}
        self.nested_models = []

        # Check if root is an array - handle specially
        if "List" in schema.get("types", []) and "array_item_schema" in schema:
            # This is a root-level array
            # Generate the item model first
            item_schema = schema["array_item_schema"]
            item_model_code = self._generate_model(item_schema, "Item", is_nested=True)
            self.nested_models.insert(0, item_model_code)

            # Generate a root model that wraps the list
            main_model = self._generate_array_root_model(model_name)
        else:
            # Generate the main model normally
            main_model = self._generate_model(schema, model_name)

        # Build the complete code
        code_parts = []

        # Add imports
        code_parts.append(self._generate_imports())
        code_parts.append("")
        code_parts.append("")

        # Add nested models first
        for nested_model in self.nested_models:
            code_parts.append(nested_model)
            code_parts.append("")
            code_parts.append("")

        # Add main model
        code_parts.append(main_model)

        return "\n".join(code_parts)

    def _generate_model(self, schema: Dict, model_name: str, is_nested: bool = False) -> str:
        """Generate a single Pydantic model class."""

        lines = []

        # Class definition
        lines.append(f"class {model_name}(BaseModel):")
        lines.append(f'    """{model_name} model"""')

        # Check if this is a dict with nested schema
        if "nested_schema" in schema and schema["nested_schema"]:
            nested_schema = schema["nested_schema"]

            # Generate fields
            for field_name, field_schema in nested_schema.items():
                field_code = self._generate_field(field_name, field_schema)
                lines.append(f"    {field_code}")

        # Check if this is a simple value type
        elif "types" in schema:
            # This is a simple type - create a single field
            field_code = self._generate_field("value", schema)
            lines.append(f"    {field_code}")

        else:
            # Empty model
            lines.append("    pass")

        return "\n".join(lines)

    def _generate_array_root_model(self, model_name: str) -> str:
        """Generate a root model that contains a list of items."""

        lines = []
        lines.append(f"class {model_name}(BaseModel):")
        lines.append(f'    """{model_name} - List of Item objects"""')

        self.imports.add("from typing import List")
        lines.append(f"    __root__: List[Item]")

        return "\n".join(lines)

    def _generate_field(self, field_name: str, field_schema: Dict) -> str:
        """Generate a single field definition."""

        # Get the Python type
        python_type = self._get_python_type(field_name, field_schema)

        # Determine if field is optional
        is_optional = field_schema.get("is_nullable", False) or self.force_optional

        if is_optional:
            python_type = f"Optional[{python_type}]"
            self.imports.add("from typing import Optional")

        # Generate Field() arguments
        field_args = []

        # Default value (required or None)
        if is_optional:
            field_args.append("None")
        else:
            field_args.append("...")

        # Add validators
        if self.include_validators:
            validators = self._get_validators(field_schema)
            field_args.extend(validators)

        # Add description
        if self.include_descriptions and "examples" in field_schema:
            examples = field_schema["examples"]
            if examples:
                description = str(examples[0])
                field_args.append(f'description="{self._escape_string(description)}"')

        # Build the field definition
        if field_args:
            field_def = f"{field_name}: {python_type} = Field({', '.join(field_args)})"
        else:
            field_def = f"{field_name}: {python_type}"

        return field_def

    def _get_python_type(self, field_name: str, field_schema: Dict) -> str:
        """Determine the Python type annotation for a field."""

        types = field_schema.get("types", [])

        if not types:
            self.imports.add("from typing import Any")
            return "Any"

        # Handle single type
        if len(types) == 1:
            type_name = types[0]

            # Handle List type
            if type_name == "List":
                item_type = self._get_array_item_type(field_schema)
                self.imports.add("from typing import List")
                return f"List[{item_type}]"

            # Handle Dict type (nested object)
            if type_name == "Dict":
                nested_model_name = self._to_class_name(field_name)
                nested_model_code = self._generate_model(
                    field_schema, nested_model_name, is_nested=True
                )
                self.nested_models.append(nested_model_code)
                return nested_model_name

            # Handle special types
            if type_name == "UUID":
                self.imports.add("from uuid import UUID")
                return "UUID"

            if type_name == "datetime":
                self.imports.add("from datetime import datetime")
                return "datetime"

            if type_name == "date":
                self.imports.add("from datetime import date")
                return "date"

            if type_name == "EmailStr":
                self.imports.add("from pydantic import EmailStr")
                return "EmailStr"

            if type_name == "HttpUrl":
                self.imports.add("from pydantic import HttpUrl")
                return "HttpUrl"

            # Basic types
            return type_name

        # Handle Union types
        self.imports.add("from typing import Union")
        union_types = [
            self._get_python_type(field_name, {"types": [t]}) for t in types if t != "None"
        ]
        return f"Union[{', '.join(union_types)}]"

    def _get_array_item_type(self, field_schema: Dict) -> str:
        """Determine the type of items in a list."""

        array_item_schema = field_schema.get("array_item_schema")

        if not array_item_schema:
            self.imports.add("from typing import Any")
            return "Any"

        item_types = array_item_schema.get("types", [])

        if not item_types:
            self.imports.add("from typing import Any")
            return "Any"

        # Single type
        if len(item_types) == 1:
            type_name = item_types[0]

            # Nested object in array
            if type_name == "Dict":
                nested_model_name = "Item"  # Generic name for array items
                nested_model_code = self._generate_model(
                    array_item_schema, nested_model_name, is_nested=True
                )
                self.nested_models.append(nested_model_code)
                return nested_model_name

            # Handle special types in array
            if type_name == "UUID":
                self.imports.add("from uuid import UUID")
                return "UUID"

            if type_name == "datetime":
                self.imports.add("from datetime import datetime")
                return "datetime"

            if type_name == "EmailStr":
                self.imports.add("from pydantic import EmailStr")
                return "EmailStr"

            if type_name == "HttpUrl":
                self.imports.add("from pydantic import HttpUrl")
                return "HttpUrl"

            return type_name

        # Multiple types - Union
        self.imports.add("from typing import Union")
        return f"Union[{', '.join(item_types)}]"

    def _get_validators(self, field_schema: Dict) -> List[str]:
        """Generate Field validators based on schema constraints."""

        validators = []

        # Numeric constraints
        if "min_value" in field_schema:
            min_val = field_schema["min_value"]
            if min_val >= 0:
                validators.append(f"ge={min_val}")
            else:
                validators.append(f"gt={min_val - 1}")

        if "max_value" in field_schema:
            max_val = field_schema["max_value"]
            validators.append(f"le={max_val}")

        # String length constraints
        if "min_length" in field_schema:
            min_len = field_schema["min_length"]
            if min_len > 0:
                validators.append(f"min_length={min_len}")

        if "max_length" in field_schema:
            max_len = field_schema["max_length"]
            validators.append(f"max_length={max_len}")

        return validators

    def _generate_imports(self) -> str:
        """Generate import statements."""

        # Sort imports by category
        pydantic_imports = []
        typing_imports = []
        stdlib_imports = []

        for imp in sorted(self.imports):
            if imp.startswith("from pydantic"):
                pydantic_imports.append(imp)
            elif imp.startswith("from typing"):
                typing_imports.append(imp)
            else:
                stdlib_imports.append(imp)

        all_imports = pydantic_imports + typing_imports + stdlib_imports
        return "\n".join(all_imports)

    def _to_class_name(self, field_name: str) -> str:
        """Convert field name to PascalCase class name."""

        # Remove invalid characters
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in field_name)

        # Convert to PascalCase
        parts = clean_name.split("_")
        return "".join(part.capitalize() for part in parts if part)

    def _escape_string(self, s: str) -> str:
        """Escape string for use in Python code."""

        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def generate_pydantic_model(
    schema: Dict,
    model_name: str = "RootModel",
    array_item_name: Optional[str] = None,
    include_validators: bool = True,
    include_descriptions: bool = True,
    force_optional: bool = False,
) -> str:
    """
    Generate Pydantic model code from schema.

    Args:
        schema: Schema dictionary from analyzer
        model_name: Name for the root model class
        array_item_name: Name for array item models (if applicable)
        include_validators: Whether to include Field validators
        include_descriptions: Whether to include field descriptions
        force_optional: Make all fields optional

    Returns:
        Generated Pydantic model code as string
    """

    generator = PydanticModelGenerator(
        include_validators=include_validators,
        include_descriptions=include_descriptions,
        force_optional=force_optional,
    )

    return generator.generate(schema, model_name)
