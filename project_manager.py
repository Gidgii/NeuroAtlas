"""Project state and repository management for Clinical Neuroscience Atlas."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_STATE_FILENAME = "PROJECT_STATE.json"
BUILD_LOG_FILENAME = "BUILD_LOG.md"
CHANGELOG_FILENAME = "CHANGELOG.md"

REQUIRED_MILESTONE_ONE_FILES = (
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    PROJECT_STATE_FILENAME,
    BUILD_LOG_FILENAME,
    CHANGELOG_FILENAME,
    "launcher.py",
    "project_manager.py",
    "milestone_manager.py",
)

REQUIRED_STATE_KEYS = (
    "version",
    "status",
    "currentPhase",
    "completedProductionSlices",
    "interactiveAnatomy",
)

DEPENDENCY_IMPORT_MAP = {
    "pydantic": "pydantic",
    "rich": "rich",
    "typer": "typer",
    "python-dotenv": "dotenv",
    "orjson": "orjson",
    "jsonschema": "jsonschema",
    "packaging": "packaging",
}


class ProjectStateError(RuntimeError):
    """Raised when project state is missing, malformed or internally inconsistent."""


@dataclass(slots=True)
class ValidationResult:
    """Structured validation result."""

    name: str
    passed: bool
    details: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(slots=True)
class ProjectManager:
    """Owns repository state, validation and append-only project records."""

    root: Path

    def __post_init__(self) -> None:
        self.root = self.root.expanduser().resolve()

    @property
    def state_path(self) -> Path:
        return self.root / PROJECT_STATE_FILENAME

    @property
    def build_log_path(self) -> Path:
        return self.root / BUILD_LOG_FILENAME

    @property
    def changelog_path(self) -> Path:
        return self.root / CHANGELOG_FILENAME

    def ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            raise ProjectStateError(f"Missing {PROJECT_STATE_FILENAME}: {self.state_path}")

        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ProjectStateError(f"{PROJECT_STATE_FILENAME} is not valid JSON: {exc}") from exc

        self._validate_state_shape(state)
        return state

    def save_state(self, state: dict[str, Any]) -> None:
        self._validate_state_shape(state)
        self.ensure_root()

        state["updated_at"] = datetime.now(UTC).isoformat()
        payload = json.dumps(state, indent=2, ensure_ascii=False) + "\n"

        fd, temp_name = tempfile.mkstemp(
            dir=self.root,
            prefix=f".{PROJECT_STATE_FILENAME}.",
            suffix=".tmp",
            text=True,
        )
        temp_path = Path(temp_name)

        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            temp_path.replace(self.state_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    def update_state(self, **changes: Any) -> dict[str, Any]:
        state = self.load_state()
        for key, value in changes.items():
            if key not in state:
                raise ProjectStateError(f"Unknown project-state key: {key}")
            state[key] = value
        self.save_state(state)
        return state

    def append_build_log(self, heading: str, entries: Iterable[str]) -> None:
        self._append_markdown(self.build_log_path, heading, entries)

    def append_changelog(self, heading: str, entries: Iterable[str]) -> None:
        self._append_markdown(self.changelog_path, heading, entries)

    def validate_required_files(
        self, required_files: Iterable[str] = REQUIRED_MILESTONE_ONE_FILES
    ) -> ValidationResult:
        missing = [name for name in required_files if not (self.root / name).is_file()]
        return ValidationResult(
            name="required_files",
            passed=not missing,
            details=["All required files are present."]
            if not missing
            else [f"Missing: {name}" for name in missing],
        )

    def validate_state(self) -> ValidationResult:
        try:
            state = self.load_state()
        except ProjectStateError as exc:
            return ValidationResult("project_state", False, [str(exc)])

        details: list[str] = []
        passed = True
        anatomy = state["interactiveAnatomy"]
        verified = anatomy["verifiedStructures"]
        if anatomy["structuresCompleted"] != len(verified):
            passed = False
            details.append("Interactive Anatomy count does not match verifiedStructures.")
        missing_details = sorted(
            structure
            for structure in verified
            if not (self.root / "app" / "data" / f"{structure}.json").is_file()
        )
        details.extend(f"Missing Interactive Anatomy detail: {name}" for name in missing_details)
        passed = passed and not missing_details

        if passed:
            details.append("Project state is structurally valid and internally consistent.")

        return ValidationResult("project_state", passed, details)

    def validate_python_syntax(self) -> ValidationResult:
        python_files = sorted(self.root.glob("*.py"))
        details: list[str] = []
        passed = True

        if not python_files:
            return ValidationResult(
                "python_syntax", False, ["No top-level Python files were found."]
            )

        for path in python_files:
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                details.append(f"Valid syntax: {path.name}")
            except (SyntaxError, UnicodeDecodeError) as exc:
                passed = False
                details.append(f"Invalid syntax: {path.name}: {exc}")

        return ValidationResult("python_syntax", passed, details)

    def validate_dependencies(self) -> ValidationResult:
        missing: list[str] = []
        present: list[str] = []

        for package, import_name in DEPENDENCY_IMPORT_MAP.items():
            if importlib.util.find_spec(import_name) is None:
                missing.append(package)
            else:
                present.append(package)

        details = [f"Available: {name}" for name in present]
        details.extend(f"Missing: {name}" for name in missing)

        return ValidationResult("dependencies", not missing, details)

    def validate_all(self) -> list[ValidationResult]:
        return [
            self.validate_required_files(),
            self.validate_state(),
            self.validate_python_syntax(),
            self.validate_dependencies(),
        ]

    def synchronise_qa_state(self, results: Iterable[ValidationResult]) -> dict[str, Any]:
        raise ProjectStateError(
            "Automatic QA-state synchronisation is disabled for the authoritative "
            "Interactive Anatomy schema; use validate --no-update-state and update "
            "the reviewed QA report explicitly."
        )

    def _validate_state_shape(self, state: Any) -> None:
        if not isinstance(state, dict):
            raise ProjectStateError("Project state must be a JSON object.")

        missing_keys = [key for key in REQUIRED_STATE_KEYS if key not in state]
        if missing_keys:
            raise ProjectStateError(
                "Project state is missing required keys: " + ", ".join(missing_keys)
            )

        if not isinstance(state["completedProductionSlices"], list):
            raise ProjectStateError("completedProductionSlices must be a list.")
        anatomy = state["interactiveAnatomy"]
        if not isinstance(anatomy, dict):
            raise ProjectStateError("interactiveAnatomy must be an object.")
        for key in ("structuresCompleted", "verifiedStructures", "nextStructure", "qaStatus"):
            if key not in anatomy:
                raise ProjectStateError(f"interactiveAnatomy is missing {key}.")
        if not isinstance(anatomy["verifiedStructures"], list):
            raise ProjectStateError("interactiveAnatomy.verifiedStructures must be a list.")

    @staticmethod
    def _append_markdown(path: Path, heading: str, entries: Iterable[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"\n## {heading}\n"]
        lines.extend(f"- {entry}\n" for entry in entries)

        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.writelines(lines)
