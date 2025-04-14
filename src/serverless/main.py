"""Main module for generating Terraform configurations for serverless functions.

This module provides functionality to:
- Parse `serverless.yml` files and extract resource configurations
- Generate Terraform project files for serverless resources
"""

# Standard Libraries
import argparse
from copy import deepcopy
from os import getenv
from pathlib import Path
from shutil import make_archive
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Any

# Third-party Libraries
import uv
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader
from loguru import logger

BASE_DIR_FUNCTIONS: Path = Path(getenv("BASE_DIR_FUNCTIONS") or "../functions").resolve()


def create_lambda_layer_archive(requirements_filepath: Path) -> Path:
    """Create a zip archive of the Python dependencies specified in the requirements.txt file."""
    logger.info(f"📦 Installing dependencies from {str(requirements_filepath)!r}")

    zip_filepath: Path = requirements_filepath.with_name("layer.zip")

    # Install the dependencies into a temporary directory and then zip them
    # The context manager ensures the temp directory is automatically cleaned up
    # Use `uv` to install the dependencies because it's extremely fast
    with TemporaryDirectory() as tmp_dir_name:
        run(  # noqa: S603
            [
                uv.find_uv_bin(),
                "pip",
                "install",
                "-r",
                str(requirements_filepath),
                "--target",
                tmp_dir_name,
            ],
            check=True,
        )

        make_archive(str(zip_filepath.with_suffix("")), "zip", root_dir=tmp_dir_name)

        return zip_filepath


def create_lambda_layers(function_path: Path) -> dict[str, str]:
    """Create Lambda layers for a given function path.

    Args:
        function_path (Path): The path to the function directory.

    Returns:
        dict[str, str]: A dictionary mapping layer names to their zip file paths.
    """
    base_dir_project: Path = BASE_DIR_FUNCTIONS.parent

    layers: dict[str, str] = {}

    rel_path: Path = function_path.relative_to(base_dir_project)

    root: Path = base_dir_project

    for part in rel_path.parts:
        root = root / part

        # Create a layer for each directory in the function path that contains a `requirements.txt` file
        requirements_filepath: Path = root / "requirements.txt"

        if requirements_filepath.exists():
            layer_name: str = part

            # Create a zip archive containing the dependencies for the layer
            layers[layer_name] = str(create_lambda_layer_archive(requirements_filepath))

    return layers


def generate_terraform_project(function_path: Path, data: dict[str, Any]) -> None:
    """Generate Terraform configuration files for a serverless function.

    Args:
        function_path (Path): The path to the function directory where Terraform files will be created.
        data (dict[str, Any]): A dictionary containing function-specific configuration data.

    Returns:
        None
    """
    # Set up the Jinja environment
    jinja_env = Environment(loader=FileSystemLoader(f"{Path(__file__).parent!s}/templates"), autoescape=True)

    function_path.mkdir(parents=True, exist_ok=True)

    data["layers"] = create_lambda_layers(function_path)

    # Load each template and write the rendered output to the corresponding file
    for name in ["lambda.tf", "provider.tf", "role.tf", "variables.tf"]:
        template = jinja_env.get_template(f"{name}.j2")
        (function_path / name).write_text(template.render(**data))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate Terraform configurations for serverless functions.")
    parser.add_argument("-c", "--clean", dest="clean", action="store_true", help="Clean up generated files")
    parser.add_argument(
        "paths",
        metavar="path",
        type=Path,
        nargs="*",
        help="One or more paths to serverless.yml files",
    )
    return parser.parse_args()


def clean_up() -> None:
    """Clean up generated files from the project directory.

    Deletes files with specific extensions such as `.zip`, `.tf`, `.tfstate`,
    and `.tfstate.backup` from the `functions` directory.
    """
    logger.info("🧹 Cleaning up generated files...")

    for ext in ["*.zip", "*.tf", "*.tfstate", "*.tfstate.backup"]:
        for path in BASE_DIR_FUNCTIONS.glob(f"**/{ext}"):
            path.unlink()
            logger.info("🧹 Deleted: {}", str(path))
    logger.success("✅ Clean-up complete")


def load_serverless_yml(file_path: Path) -> dict[str, Any]:
    """Load and parse a serverless.yml file.

    Args:
        file_path (Path): The path to the serverless.yml file.

    Returns:
        dict[str, Any]: A dictionary representation of the YAML file.
    """
    with file_path.open() as f:
        return dict(yaml.safe_load(f))


def generate_terraform_projects(serverless_configs: list[Path]) -> None:
    """Generate Terraform configurations for the provided serverless.yml files.

    Args:
        serverless_configs (list[Path]): A list of paths to serverless.yml files.
    """
    for sls_file in serverless_configs:
        if not sls_file.exists():
            logger.error(f"❌ File not found: {sls_file}")
            continue

        logger.info("📜 Parsing serverless.yml file: {}", str(sls_file))
        sls: dict[str, Any] = load_serverless_yml(sls_file)

        # Get the provider properties and set applicable defaults
        provider_properties: dict[str, Any] = sls.setdefault("provider", {})
        provider_properties.setdefault("environment", {})
        provider_properties.setdefault("events", [])
        provider_properties.setdefault("handler")
        provider_properties.setdefault("memorySize", 256)
        provider_properties.setdefault("runtime", "python3.9")
        provider_properties.setdefault("timeout", 10)

        functions: dict[str, Any] = sls.setdefault("functions", {})
        function_names: list[str] = []

        for name, function_properties in functions.items():
            logger.info("📜 Generating Terraform configs for: {}", name)

            function_names.append(name)
            function_path: Path = BASE_DIR_FUNCTIONS / name

            # Use the provider properties as defaults and override with function-specific properties
            # Use deepcopy to avoid modifying the original provider dict
            data: dict[str, Any] = deepcopy(provider_properties)
            data.update(function_properties)
            data["function_name"] = name

            generate_terraform_project(function_path, data)

        # generate_root_tf(function_names)
        logger.success(f"✅ Terraform modules and configs generated successfully for {sls_file}.")


def main() -> None:
    """Main function to generate Terraform configurations for serverless functions."""
    args: argparse.Namespace = parse_args()

    if args.clean:
        clean_up()
        return

    # Generate Terraform projects for the specified serverless.yml files
    generate_terraform_projects(args.paths)


if __name__ == "__main__":
    main()
