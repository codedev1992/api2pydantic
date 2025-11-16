"""
Fetch JSON data from URLs, files, or curl commands.
"""

import json
import subprocess
import requests
from typing import Union
from pathlib import Path


def fetch_json(source: str) -> Union[dict, list]:
    """
    Fetch JSON data from various sources.

    Args:
        source: Can be a URL, file path, or curl command

    Returns:
        Parsed JSON data (dict or list)

    Raises:
        ValueError: If source format is invalid or data cannot be parsed
    """
    source = source.strip()

    # Handle curl commands
    if source.startswith("curl "):
        return _fetch_from_curl(source)

    # Handle file:// protocol or 'file' prefix
    if source.startswith("file://"):
        file_path = source[7:]
        return _fetch_from_file(file_path)
    elif source.startswith("file "):
        file_path = source[5:].strip()
        return _fetch_from_file(file_path)

    # Handle URLs (http/https)
    if source.startswith("http://") or source.startswith("https://"):
        return _fetch_from_url(source)

    # Try as file path
    if Path(source).exists():
        return _fetch_from_file(source)

    # Try to parse as JSON string directly
    try:
        return json.loads(source)
    except json.JSONDecodeError:
        pass

    raise ValueError(
        f"Could not determine source type for: {source}\n"
        "Expected: URL (http://...), file path, 'file <path>', or curl command"
    )


def _fetch_from_url(url: str) -> Union[dict, list]:
    """Fetch JSON from a URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch from URL: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Response is not valid JSON: {e}")


def _fetch_from_file(file_path: str) -> Union[dict, list]:
    """Fetch JSON from a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"File contains invalid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")


def _fetch_from_curl(curl_command: str) -> Union[dict, list]:
    """Execute curl command and parse JSON response."""
    try:
        # Execute curl command
        result = subprocess.run(
            curl_command, shell=True, capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            raise ValueError(f"curl command failed: {result.stderr}")

        # Parse JSON from output
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise ValueError("curl command timed out")
    except json.JSONDecodeError as e:
        raise ValueError(f"curl response is not valid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Failed to execute curl command: {e}")


def fetch_multiple_sources(sources: list) -> list:
    """
    Fetch JSON from multiple sources for better type inference.

    Args:
        sources: List of source strings (URLs, files, etc.)

    Returns:
        List of parsed JSON data
    """
    results = []
    for source in sources:
        try:
            data = fetch_json(source)
            results.append(data)
        except Exception as e:
            print(f"Warning: Failed to fetch from {source}: {e}")

    if not results:
        raise ValueError("Failed to fetch data from any source")

    return results
