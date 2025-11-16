# API-to-Pydantic

🚀 Automatically generate Pydantic models from API responses, JSON files, or curl commands.

## Features

✨ **Smart Type Inference** - Automatically detects correct Python types from sample data  
🔍 **Pattern Recognition** - Identifies emails, URLs, UUIDs, datetimes, and more  
📦 **Nested Structures** - Handles complex nested objects and arrays  
✅ **Validators** - Generates Field validators based on data patterns  
🎯 **Optional Detection** - Identifies optional fields from null values  
🔄 **Enum Recognition** - Detects limited value sets and creates enums  
📝 **Documentation** - Adds helpful docstrings to generated models

## Installation

```bash
pip install api2pydantic
```

Or install from source:

```bash
git clone https://github.com/codedev1992/api2pydantic.git
cd api2pydantic
pip install -e .
```

## Quick Start

### From a URL
```bash
api2pydantic https://api.example.com/users
```

### using Piple
```bash 
curl https://api.example.com/users | api2pydantic
```

### From curl command
```bash
api2pydantic curl https://api.example.com/users -H "Authorization: Bearer token"
```

### From JSON file
```bash
api2pydantic file data.json
```

### From stdin
```bash
echo '{"name": "John", "age": 30}' | api2pydantic
```

### Save to file
```bash
api2pydantic https://api.example.com/users --output models.py
```

### Custom model name
```bash
api2pydantic https://api.example.com/users --model-name UserResponse
```

## Examples

**Input JSON:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "John Doe",
  "age": 30,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "tags": ["python", "pydantic"],
  "profile": {
    "bio": "Software Developer",
    "website": "https://example.com"
  }
}
```

**Generated Pydantic Model:**
```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class Profile(BaseModel):
    """Profile model"""
    bio: str = Field(..., description="Software Developer")
    website: HttpUrl = Field(..., description="https://example.com")


class RootModel(BaseModel):
    """RootModel model"""
    id: UUID = Field(..., description="123e4567-e89b-12d3-a456-426614174000")
    email: EmailStr = Field(..., description="user@example.com")
    name: str = Field(..., min_length=1, description="John Doe")
    age: int = Field(..., ge=0, description="30")
    is_active: bool = Field(..., description="True")
    created_at: datetime = Field(..., description="2024-01-15T10:30:00Z")
    tags: List[str] = Field(..., description="['python', 'pydantic']")
    profile: Profile = Field(..., description="Profile model")
```

## Advanced Usage

### Multiple samples for better inference
```bash
# Analyze multiple API responses to improve type detection
api2pydantic https://api.example.com/users/1 \
             https://api.example.com/users/2 \
             https://api.example.com/users/3
```

### Options
```bash
api2pydantic --help

Options:
  --output, -o          Output file path
  --model-name, -m      Custom model name (default: RootModel)
  --array-item-name     Name for array item models
  --no-validators       Skip generating validators
  --no-descriptions     Skip adding descriptions
  --force-optional      Make all fields optional
```

## How It Works

1. **Fetch** - Retrieves JSON data from URL, file, or curl command
2. **Analyze** - Examines values to infer types and detect patterns
3. **Generate** - Creates Pydantic model with proper type hints
4. **Validate** - Adds field validators based on data constraints
5. **Format** - Outputs clean, formatted Python code

## Type Detection

The tool intelligently detects:

- **Primitives**: str, int, float, bool, None
- **Collections**: List, Dict, Set
- **Special Types**: UUID, datetime, date, time
- **Validated Types**: EmailStr, HttpUrl
- **Patterns**: Enum detection from limited value sets
- **Optionals**: Fields with null values
- **Unions**: Mixed types in arrays

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your_feature_name`)
3. Commit your changes (`git commit -m 'Add some your_feature_name'`)
4. Push to the branch (`git push origin feature/your_feature_name`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repo
git clone https://github.com/codedev1992/api2pydantic.git
cd api2pydantic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
flake8 api2pydantic tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the amazing [Pydantic](https://pydantic-docs.helpmanual.io/) library
- Built to solve the tedious task of manually writing models

## Roadmap

- [ ] Support for JSON Schema output
- [ ] GraphQL schema support
- [ ] OpenAPI spec generation
- [ ] VS Code extension
- [ ] Web UI for online conversion
- [ ] Support for more validation patterns

## Support

⭐ Star this repo if you find it helpful!  
🐛 [Report bugs](https://github.com/codedev1992/api2pydantic/issues)  
💡 [Request features](https://github.com/codedev1992/api2pydantic/issues)

---

Made with ❤️