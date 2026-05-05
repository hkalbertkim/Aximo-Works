#!/usr/bin/env python3
"""Validate the minimal Aximo Control configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
REQUIRED_CONFIGS = {
    "projects": CONFIG_DIR / "projects.yaml",
    "machines": CONFIG_DIR / "machines.yaml",
    "departments": CONFIG_DIR / "departments.yaml",
    "tools": CONFIG_DIR / "tools.yaml",
}


def load_yaml_module() -> Any | None:
    try:
        import yaml  # type: ignore
    except ImportError:
        return None
    return yaml


def main() -> int:
    print("Aximo Control config validation")
    print(f"Root: {ROOT}")

    missing = [path for path in REQUIRED_CONFIGS.values() if not path.exists()]
    if missing:
        print("\nMissing required config files:")
        for path in missing:
            print(f"- {path.relative_to(ROOT)}")
        return 1

    print("\nRequired files:")
    for name, path in REQUIRED_CONFIGS.items():
        print(f"- {name}: {path.relative_to(ROOT)}")

    yaml = load_yaml_module()
    if yaml is None:
        print(
            "\nPyYAML is optional and is not installed. File existence checks passed, "
            "but YAML parsing was skipped."
        )
        print("Install PyYAML only if parsed validation is needed: python3 -m pip install PyYAML")
        return 0

    print("\nParsed YAML:")
    total_records = 0
    for name, path in REQUIRED_CONFIGS.items():
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        records = data.get(name, [])
        if not isinstance(records, list):
            print(f"- {path.relative_to(ROOT)}: expected top-level '{name}' list")
            return 1
        total_records += len(records)
        print(f"- {name}: {len(records)} records")

    print(f"\nValidation summary: 4 files found, {total_records} records parsed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
