from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int | None
    special_needs: list[str] = field(default_factory=list)
    daily_needs: list[str] = field(default_factory=list)

    def needs_medication(self) -> bool:
        pass

    def requires_extra_care(self) -> bool:
        pass

    def care_summary(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low" | "medium" | "high"
    task_type: str
    required: bool
    earliest_start: str | None = None
    latest_end: str | None = None

    def priority_value(self) -> int:
        pass

    def fits_in_window(self, start: str, end: str) -> bool:
        pass

    def is_required(self) -> bool:
        pass

    def can_be_scheduled(self, available_minutes: int) -> bool:
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        preferences: dict,
        available_minutes: int,
        available_windows: list[tuple[str, str]] | None = None,
    ) -> None:
        self.name = name
        self.preferences = preferences
        self.available_minutes = available_minutes
        self.available_windows = available_windows or []

    def is_available(self, duration: int) -> bool:
        pass

    def prefers_time_of_day(self, time_of_day: str) -> bool:
        pass

    def remaining_availability(self) -> int:
        pass

    def use_minutes(self, duration: int) -> None:
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_schedule(self) -> list[dict]:
        pass

    def select_tasks(self) -> list[Task]:
        pass

    def order_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def allocate_time(self, tasks: list[Task]) -> list[dict]:
        pass

    def explain_plan(self, schedule: list[dict]) -> str:
        pass
