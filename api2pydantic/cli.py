"""
Command-line interface for api2pydantic.
"""

import sys
import click
from typing import Optional
from api2pydantic.fetcher import fetch_json
from api2pydantic.analyzer import analyze_json
from api2pydantic.generator import generate_pydantic_model


@click.command()
@click.argument("source", required=False)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--model-name", "-m", default="RootModel", help="Custom model name")
@click.option("--array-item-name", default=None, help="Name for array item models")
@click.option("--no-validators", is_flag=True, help="Skip generating validators")
@click.option("--no-descriptions", is_flag=True, help="Skip adding descriptions")
@click.option("--force-optional", is_flag=True, help="Make all fields optional")
def main(
    source: Optional[str],
    output: Optional[str],
    model_name: str,
    array_item_name: Optional[str],
    no_validators: bool,
    no_descriptions: bool,
    force_optional: bool,
) -> None:
    """
    Generate Pydantic models from API responses, JSON files, or curl commands.

    Examples:

        api2pydantic https://api.example.com/users

        api2pydantic 'curl https://api.example.com/users -H "Authorization: Bearer token"'

        api2pydantic file data.json

        echo '{"name": "John"}' | api2pydantic
    """
    try:
        # Fetch JSON data
        if source is None:
            # Read from stdin
            if sys.stdin.isatty():
                click.echo("Error: No input provided. Use --help for usage information.", err=True)
                sys.exit(1)
            json_data = sys.stdin.read()
        else:
            json_data = fetch_json(source)

        # Analyze the JSON structure
        schema = analyze_json(json_data)

        # Generate Pydantic model
        code = generate_pydantic_model(
            schema=schema,
            model_name=model_name,
            array_item_name=array_item_name,
            include_validators=not no_validators,
            include_descriptions=not no_descriptions,
            force_optional=force_optional,
        )

        # Output the generated code
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(code)
            click.echo(f"✓ Generated Pydantic model saved to: {output}")
        else:
            click.echo(code)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
