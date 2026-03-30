from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

buddy = Pet(
    name="Buddy",
    species="Dog",
    age=4,
    daily_needs=["Morning walk", "Feeding"],
    special_needs=["Medication - joint supplement"],
)

luna = Pet(
    name="Luna",
    species="Cat",
    age=2,
    daily_needs=["Feeding"],
    special_needs=[],
)

# ---------------------------------------------------------------------------
# Tasks — manually created with varied times
# ---------------------------------------------------------------------------

# Buddy's tasks
morning_walk = Task(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    task_type="exercise",
    required=True,
    earliest_start="07:00",
    latest_end="09:00",
)

joint_med = Task(
    title="Joint supplement",
    duration_minutes=5,
    priority="high",
    task_type="medication",
    required=True,
    earliest_start="08:00",
    latest_end="09:00",
)

buddy_feeding = Task(
    title="Buddy — feeding",
    duration_minutes=10,
    priority="medium",
    task_type="feeding",
    required=True,
    earliest_start="07:30",
    latest_end="08:30",
)

# Luna's tasks
luna_feeding = Task(
    title="Luna — feeding",
    duration_minutes=10,
    priority="medium",
    task_type="feeding",
    required=True,
    earliest_start="08:00",
    latest_end="09:00",
)

enrichment = Task(
    title="Luna — play / enrichment",
    duration_minutes=20,
    priority="low",
    task_type="enrichment",
    required=False,
    earliest_start="17:00",
    latest_end="19:00",
)

buddy.add_task(morning_walk)
buddy.add_task(joint_med)
buddy.add_task(buddy_feeding)

luna.add_task(luna_feeding)
luna.add_task(enrichment)

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

owner = Owner(
    name="Alex",
    preferences={"morning": True, "evening": False},
    available_minutes=90,
    available_windows=[("07:00", "09:00"), ("17:00", "19:00")],
)

owner.add_pet(buddy)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner=owner)
schedule = scheduler.generate_schedule()

print("=" * 45)
print("         PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 45)
print(scheduler.explain_plan(schedule))
print("=" * 45)
