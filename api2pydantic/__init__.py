"""
API-to-Pydantic: Automatically generate Pydantic models from API responses.
"""

__version__ = "0.1.0"
__author__ = "Sornalingam"
__email__ = "devcode1992@gmail.com"

from api2pydantic.analyzer import analyze_json
from api2pydantic.generator import generate_pydantic_model
from api2pydantic.fetcher import fetch_json

__all__ = ["analyze_json", "generate_pydantic_model", "fetch_json"]
