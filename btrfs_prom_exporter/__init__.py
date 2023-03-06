# Copyright (c) 2023 Philip May
# This software is distributed under the terms of the MIT license
# which is available at https://opensource.org/licenses/MIT

"""btrfs_prom_exporter main package."""

from btrfs_prom_exporter.btrfs_prom_exporter import main


# Versioning follows the Semantic Versioning Specification https://semver.org/ and
# PEP 440 -- Version Identification and Dependency Specification: https://www.python.org/dev/peps/pep-0440/  # noqa: E501
__version__ = "0.0.1rc5"

__all__ = ["__version__", "main"]


def cli_main() -> None:
    """CLI entry point."""
    main()
