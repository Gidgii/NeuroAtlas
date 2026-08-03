"""Milestone definitions and completion controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from project_manager import ProjectManager, ProjectStateError, ValidationResult


@dataclass(frozen=True, slots=True)
class MilestoneDefinition:
    """Immutable milestone definition."""

    milestone_id: int
    name: str
    required_files: tuple[str, ...]
    description: str


MILESTONES: dict[int, MilestoneDefinition] = {
    1: MilestoneDefinition(
        milestone_id=1,
        name="Repository Foundation",
        required_files=(
            "README.md",
            "requirements.txt",
            "pyproject.toml",
            "PROJECT_STATE.json",
            "BUILD_LOG.md",
            "CHANGELOG.md",
            "launcher.py",
            "project_manager.py",
            "milestone_manager.py",
        ),
        description="Establish repository governance, state tracking and build controls.",
    ),
    2: MilestoneDefinition(
        milestone_id=2,
        name="PWA Application Shell",
        required_files=(),
        description="Create the installable, offline-capable mobile-first application shell.",
    ),
    3: MilestoneDefinition(
        milestone_id=3,
        name="Level 1 — The Building Blocks",
        required_files=(),
        description="Complete Level 1 curriculum, illustrations, interactions and QA.",
    ),
    4: MilestoneDefinition(
        milestone_id=4,
        name="Level 2 — Meet the Brain",
        required_files=(),
        description="Complete Level 2 curriculum, illustrations, interactions and QA.",
    ),
    5: MilestoneDefinition(
        milestone_id=5,
        name="Level 3 — Meet the Characters",
        required_files=(),
        description="Complete Level 3 curriculum, illustrations, interactions and QA.",
    ),
}


class MilestoneManager:
    """Evaluates and advances repository milestones."""

    def __init__(self, project_manager: ProjectManager) -> None:
        self.project = project_manager

    def list_milestones(self) -> list[dict[str, Any]]:
        state = self.project.load_state()
        current_id = int(state["current_milestone"]["id"])

        rows: list[dict[str, Any]] = []
        for milestone_id, definition in sorted(MILESTONES.items()):
            if milestone_id < current_id:
                status = "completed"
            elif milestone_id == current_id:
                status = state["current_milestone"]["status"]
            else:
                status = "pending"

            rows.append(
                {
                    "id": milestone_id,
                    "name": definition.name,
                    "description": definition.description,
                    "status": status,
                }
            )
        return rows

    def status(self, milestone_id: int) -> dict[str, Any]:
        definition = self._get_definition(milestone_id)
        state = self.project.load_state()

        required_files_result = self.project.validate_required_files(
            definition.required_files
        )
        validation_results = self.project.validate_all() if milestone_id == 1 else []

        return {
            "id": milestone_id,
            "name": definition.name,
            "description": definition.description,
            "is_current": int(state["current_milestone"]["id"]) == milestone_id,
            "recorded_status": self._recorded_status(state, milestone_id),
            "required_files": list(definition.required_files),
            "required_files_passed": required_files_result.passed,
            "validation": [result.as_dict() for result in validation_results],
        }

    def can_complete(self, milestone_id: int) -> tuple[bool, list[ValidationResult]]:
        definition = self._get_definition(milestone_id)
        state = self.project.load_state()
        current_id = int(state["current_milestone"]["id"])

        if milestone_id != current_id:
            return (
                False,
                [
                    ValidationResult(
                        "milestone_sequence",
                        False,
                        [
                            f"Milestone {milestone_id} cannot be completed while "
                            f"Milestone {current_id} is current."
                        ],
                    )
                ],
            )

        results = [
            self.project.validate_required_files(definition.required_files),
            self.project.validate_state(),
            self.project.validate_python_syntax(),
            self.project.validate_dependencies(),
        ]
        return all(result.passed for result in results), results

    def complete(self, milestone_id: int) -> dict[str, Any]:
        allowed, results = self.can_complete(milestone_id)
        self.project.synchronise_qa_state(results)

        if not allowed:
            failures = [
                detail
                for result in results
                if not result.passed
                for detail in result.details
            ]
            raise ProjectStateError(
                "Milestone completion blocked:\n- " + "\n- ".join(failures)
            )

        state = self.project.load_state()
        next_id = milestone_id + 1
        next_definition = MILESTONES.get(next_id)

        if next_definition is None:
            state["current_milestone"] = {
                "id": milestone_id,
                "name": MILESTONES[milestone_id].name,
                "status": "completed",
            }
            state["next_recommended_task"] = "All defined milestones are complete."
        else:
            state["current_milestone"] = {
                "id": next_id,
                "name": next_definition.name,
                "status": "in_progress",
            }
            state["next_recommended_task"] = (
                f"Begin Milestone {next_id}: {next_definition.name}."
            )

        state["build_status"]["state"] = "milestone_completed"
        state["qa_status"]["state"] = "passed"
        state["known_issues"] = [
            issue
            for issue in state["known_issues"]
            if "dependencies" not in issue.lower()
            and "runtime cli validation" not in issue.lower()
        ]

        self.project.save_state(state)
        self.project.append_build_log(
            f"Milestone {milestone_id} completed",
            [
                "All required files were present.",
                "Project state validation passed.",
                "Python syntax validation passed.",
                "Dependency validation passed.",
            ],
        )
        self.project.append_changelog(
            f"Milestone {milestone_id}",
            [f"Completed {MILESTONES[milestone_id].name}."],
        )
        return state

    @staticmethod
    def _recorded_status(state: dict[str, Any], milestone_id: int) -> str:
        current_id = int(state["current_milestone"]["id"])
        if milestone_id < current_id:
            return "completed"
        if milestone_id == current_id:
            return str(state["current_milestone"]["status"])
        return "pending"

    @staticmethod
    def _get_definition(milestone_id: int) -> MilestoneDefinition:
        try:
            return MILESTONES[milestone_id]
        except KeyError as exc:
            raise ProjectStateError(
                f"Unknown milestone {milestone_id}. "
                f"Valid milestones: {', '.join(map(str, sorted(MILESTONES)))}"
            ) from exc
