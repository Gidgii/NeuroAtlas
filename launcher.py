"""Command-line launcher for Clinical Neuroscience Atlas repository tooling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from milestone_manager import MilestoneManager
from project_manager import ProjectManager, ProjectStateError

app = typer.Typer(
    name="clinical-neuroscience-atlas",
    help="Build, validate and manage the Clinical Neuroscience Atlas repository.",
    no_args_is_help=True,
)
milestone_app = typer.Typer(help="Inspect and manage milestones.")
app.add_typer(milestone_app, name="milestone")

console = Console()


def _manager(root: Path) -> ProjectManager:
    return ProjectManager(root=root)


def _fail(message: str, exit_code: int = 1) -> None:
    console.print(Panel(message, title="Clinical Neuroscience Atlas", style="red"))
    raise typer.Exit(exit_code)


@app.command()
def status(
    root: Annotated[
        Path,
        typer.Option(
            "--root",
            help="Repository root.",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = Path("."),
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
) -> None:
    """Display the authoritative project state."""
    try:
        state = _manager(root).load_state()
    except ProjectStateError as exc:
        _fail(str(exc))

    if as_json:
        console.print_json(json.dumps(state, ensure_ascii=False))
        return

    milestone = state["current_milestone"]
    table = Table(title="Clinical Neuroscience Atlas")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Version", str(state["current_version"]))
    table.add_row(
        "Milestone",
        f"{milestone['id']}: {milestone['name']} ({milestone['status']})",
    )
    table.add_row("Build", str(state["build_status"]["state"]))
    table.add_row("QA", str(state["qa_status"]["state"]))
    table.add_row("Known issues", str(len(state["known_issues"])))
    table.add_row("Next task", str(state["next_recommended_task"]))
    console.print(table)


@app.command()
def validate(
    root: Annotated[
        Path,
        typer.Option(
            "--root",
            help="Repository root.",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = Path("."),
    update_state: Annotated[
        bool,
        typer.Option(
            "--update-state/--no-update-state",
            help="Persist validation results to PROJECT_STATE.json.",
        ),
    ] = True,
) -> None:
    """Run repository validation."""
    manager = _manager(root)

    try:
        results = manager.validate_all()
        if update_state:
            manager.synchronise_qa_state(results)
    except ProjectStateError as exc:
        _fail(str(exc))

    table = Table(title="Validation")
    table.add_column("Check", style="bold")
    table.add_column("Result")
    table.add_column("Details")

    for result in results:
        table.add_row(
            result.name,
            "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]",
            "\n".join(result.details) or "No details.",
        )

    console.print(table)

    if not all(result.passed for result in results):
        raise typer.Exit(1)


@milestone_app.command("list")
def list_milestones(
    root: Annotated[
        Path,
        typer.Option("--root", file_okay=False, dir_okay=True, resolve_path=True),
    ] = Path("."),
) -> None:
    """List all defined milestones."""
    try:
        rows = MilestoneManager(_manager(root)).list_milestones()
    except ProjectStateError as exc:
        _fail(str(exc))

    table = Table(title="Milestones")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Description")

    for row in rows:
        table.add_row(
            str(row["id"]),
            str(row["name"]),
            str(row["status"]),
            str(row["description"]),
        )
    console.print(table)


@milestone_app.command("status")
def milestone_status(
    milestone_id: Annotated[int, typer.Argument(min=1)],
    root: Annotated[
        Path,
        typer.Option("--root", file_okay=False, dir_okay=True, resolve_path=True),
    ] = Path("."),
) -> None:
    """Display status for one milestone."""
    try:
        data = MilestoneManager(_manager(root)).status(milestone_id)
    except ProjectStateError as exc:
        _fail(str(exc))

    console.print_json(json.dumps(data, indent=2, ensure_ascii=False))


@milestone_app.command("complete")
def milestone_complete(
    milestone_id: Annotated[int, typer.Argument(min=1)],
    root: Annotated[
        Path,
        typer.Option("--root", file_okay=False, dir_okay=True, resolve_path=True),
    ] = Path("."),
) -> None:
    """Complete the current milestone after all checks pass."""
    try:
        state = MilestoneManager(_manager(root)).complete(milestone_id)
    except ProjectStateError as exc:
        _fail(str(exc))

    next_milestone = state["current_milestone"]
    console.print(
        Panel(
            f"Milestone {milestone_id} completed.\n"
            f"Current milestone: {next_milestone['id']}: "
            f"{next_milestone['name']}.",
            title="Success",
            style="green",
        )
    )


if __name__ == "__main__":
    app()
