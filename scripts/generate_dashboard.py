#!/usr/bin/env python3
"""Generate the portfolio dashboard from local YAML config."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_FILE = ROOT / "config" / "projects.yaml"
MACHINES_FILE = ROOT / "config" / "machines.yaml"
DASHBOARD_FILE = ROOT / "dashboards" / "dashboard.md"


def load_yaml_module() -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is optional but required to generate dashboards from YAML. "
            "Install it with: python3 -m pip install PyYAML"
        ) from exc
    return yaml


def read_yaml(path: Path) -> dict[str, Any]:
    yaml = load_yaml_module()
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a YAML mapping")
    return data


def yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def join_list(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("\n", " ") for value in values) + " |"


def build_dashboard(projects: list[dict[str, Any]], machines: list[dict[str, Any]]) -> str:
    lines = [
        "# Aximo Control Dashboard",
        "",
        f"Generated on {date.today().isoformat()} from `config/projects.yaml` and `config/machines.yaml`.",
        "",
        "## Portfolio Summary",
        "",
        "| Project | Status | Priority | Owner Machine | Current Focus | Next Action | Blocked |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for project in projects:
        lines.append(
            table_row(
                [
                    project.get("name", project.get("id", "")),
                    project.get("status", ""),
                    project.get("priority", ""),
                    project.get("owner_machine", ""),
                    project.get("current_focus", ""),
                    project.get("next_action", ""),
                    yes_no(project.get("blocked", False)),
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Machine Load",
            "",
            "| Machine | Role | Status | Max Parallel Tasks | Active Projects |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    for machine in machines:
        lines.append(
            table_row(
                [
                    machine.get("id", ""),
                    machine.get("role", ""),
                    machine.get("status", ""),
                    machine.get("max_parallel_tasks", ""),
                    join_list(machine.get("active_projects", [])),
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Open Attention",
            "",
            "- Review high-priority projects for next executable tasks.",
            "- Confirm whether any project needs an approval entry before work begins.",
            "- Keep project reports updated after meaningful changes.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if not PROJECTS_FILE.exists() or not MACHINES_FILE.exists():
        print("Required config files are missing. Expected config/projects.yaml and config/machines.yaml.")
        return 1

    try:
        projects_data = read_yaml(PROJECTS_FILE)
        machines_data = read_yaml(MACHINES_FILE)
    except RuntimeError as exc:
        print(exc)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Could not read config: {exc}")
        return 1

    projects = projects_data.get("projects", [])
    machines = machines_data.get("machines", [])
    if not isinstance(projects, list) or not isinstance(machines, list):
        print("Expected top-level 'projects' and 'machines' lists.")
        return 1

    DASHBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_FILE.write_text(build_dashboard(projects, machines), encoding="utf-8")
    print(f"Generated {DASHBOARD_FILE.relative_to(ROOT)} from {len(projects)} projects and {len(machines)} machines.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
