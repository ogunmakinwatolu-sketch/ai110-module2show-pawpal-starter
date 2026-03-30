from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

# Enforced time format for all time strings across the system (HH:MM, 24-hour)
TIME_FORMAT = "%H:%M"


# ---------------------------------------------------------------------------
# Task — a single schedulable care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    task_type: str
    required: bool
    earliest_start: str | None = None   # must follow TIME_FORMAT ("%H:%M")
    latest_end: str | None = None       # must follow TIME_FORMAT ("%H:%M")
    completed: bool = False

    @staticmethod
    def _parse_time(time_str: str) -> datetime:
        """Parse a time string using TIME_FORMAT so all comparisons are consistent."""
        return datetime.strptime(time_str, TIME_FORMAT)

    def priority_value(self) -> int:
        """Map priority label to a numeric value for sorting."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)

    def fits_in_window(self, start: str, end: str) -> bool:
        """Return True if the task's timing constraints fall within start–end."""
        window_start = self._parse_time(start)
        window_end = self._parse_time(end)
        if self.earliest_start and self._parse_time(self.earliest_start) < window_start:
            return False
        if self.latest_end and self._parse_time(self.latest_end) > window_end:
            return False
        return True

    def is_required(self) -> bool:
        """Kept as a method for polymorphic access; returns self.required."""
        return self.required

    def can_be_scheduled(self, available_minutes: int) -> bool:
        """Return True if the task fits within the given available time."""
        return self.duration_minutes <= available_minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


# ---------------------------------------------------------------------------
# Pet — stores pet details and a list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int | None
    special_needs: list[str] = field(default_factory=list)
    daily_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def needs_medication(self) -> bool:
        """Return True if any special need mentions medication."""
        return any(
            "medication" in need.lower() or "med" in need.lower()
            for need in self.special_needs
        )

    def requires_extra_care(self) -> bool:
        """Return True if the pet has any special needs."""
        return len(self.special_needs) > 0

    def care_summary(self) -> str:
        """Return a human-readable summary of the pet's care profile."""
        age_str = str(self.age) if self.age is not None else "unknown"
        lines = [f"{self.name} ({self.species}, age {age_str})"]
        if self.daily_needs:
            lines.append(f"  Daily needs: {', '.join(self.daily_needs)}")
        if self.special_needs:
            lines.append(f"  Special needs: {', '.join(self.special_needs)}")
        if not self.daily_needs and not self.special_needs:
            lines.append("  No specific needs recorded.")
        return "\n".join(lines)

    def add_task(self, task: Task) -> None:
        """Attach an existing Task to this pet."""
        self.tasks.append(task)

    def generate_tasks(self) -> list[Task]:
        """Convert daily_needs and special_needs into Task objects and attach them.

        Establishes the Pet -> Task relationship from the UML: tasks originate
        from a pet's declared needs rather than being created independently.
        """
        generated: list[Task] = []

        for need in self.daily_needs:
            generated.append(Task(
                title=need,
                duration_minutes=15,
                priority="medium",
                task_type="daily",
                required=True,
            ))

        for need in self.special_needs:
            priority = "high" if "medication" in need.lower() else "medium"
            generated.append(Task(
                title=need,
                duration_minutes=10,
                priority=priority,
                task_type="special",
                required=True,
            ))

        self.tasks.extend(generated)
        return generated


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides access to all their tasks
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        preferences: dict,
        available_minutes: int,
        available_windows: list[tuple[str, str]] | None = None,
    ) -> None:
        """Initialise owner with identity, time budget, preferences, and an empty pet list."""
        self.name = name
        self.preferences = preferences          # e.g. {"morning": True, "evening": False}
        self.available_minutes = available_minutes
        self.available_windows = available_windows or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten and return every task across all owned pets.

        This is the primary retrieval point for the Scheduler — it only needs
        to call owner.all_tasks() rather than iterating pets itself.
        """
        return [task for pet in self.pets for task in pet.tasks]

    def is_available(self, duration: int) -> bool:
        """Return True if the owner has enough minutes left for the given duration."""
        return self.remaining_availability() >= duration

    def prefers_time_of_day(self, time_of_day: str) -> bool:
        """Return the owner's preference for a given time of day label."""
        return bool(self.preferences.get(time_of_day, False))

    def remaining_availability(self) -> int:
        """Return how many minutes the owner still has available."""
        return self.available_minutes

    def use_minutes(self, duration: int) -> None:
        """Deduct duration from available_minutes.

        Raises ValueError if duration exceeds remaining availability so
        available_minutes can never go negative.
        """
        if duration > self.available_minutes:
            raise ValueError(
                f"Cannot use {duration} minutes — only "
                f"{self.available_minutes} remaining."
            )
        self.available_minutes -= duration


# ---------------------------------------------------------------------------
# Scheduler — retrieves, organises, and manages tasks across all pets
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialise the scheduler with an owner whose pets and tasks it will manage."""
        self.owner = owner

    def select_tasks(self) -> list[Task]:
        """Return tasks that are incomplete and fit within remaining availability."""
        return [
            task for task in self.owner.all_tasks()
            if not task.completed
            and task.can_be_scheduled(self.owner.remaining_availability())
        ]

    def order_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks: required first, then by descending priority value."""
        return sorted(tasks, key=lambda t: (not t.is_required(), -t.priority_value()))

    def allocate_time(self, tasks: list[Task]) -> list[dict]:
        """Assign tasks to the schedule while owner time permits.

        Each allocated task is recorded as a dict and deducted from the
        owner's available minutes.
        """
        schedule = []
        for task in tasks:
            if self.owner.is_available(task.duration_minutes):
                self.owner.use_minutes(task.duration_minutes)
                schedule.append({
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "required": task.required,
                    "task_type": task.task_type,
                })
        return schedule

    def generate_schedule(self) -> list[dict]:
        """Run the full pipeline: select → order → allocate → validate."""
        selected = self.select_tasks()
        ordered = self.order_tasks(selected)
        schedule = self.allocate_time(ordered)
        self.validate_schedule(schedule)
        return schedule

    def validate_schedule(self, schedule: list[dict]) -> bool:
        """Verify available_minutes did not go negative after allocation.

        allocate_time() is the primary guard via use_minutes(); this is a
        defensive sanity check that remaining availability is non-negative.
        """
        if self.owner.remaining_availability() < 0:
            raise RuntimeError("Schedule overran owner's available time budget.")
        return True

    def explain_plan(self, schedule: list[dict]) -> str:
        """Return a human-readable explanation of the generated schedule."""
        if not schedule:
            return f"{self.owner.name} has no tasks scheduled today."
        lines = [f"Schedule for {self.owner.name}:"]
        for i, entry in enumerate(schedule, 1):
            req_label = "required" if entry["required"] else "optional"
            lines.append(
                f"  {i}. {entry['title']} — {entry['duration_minutes']} min "
                f"[{entry['priority']} priority, {req_label}]"
            )
        lines.append(
            f"\nTime remaining after scheduling: "
            f"{self.owner.remaining_availability()} minutes"
        )
        return "\n".join(lines)
