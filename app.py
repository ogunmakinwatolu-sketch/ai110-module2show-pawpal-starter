import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — initialise Owner and Pet exactly once per browser session
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        preferences={"morning": True, "evening": False},
        available_minutes=120,
    )

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", species="dog", age=None)
    st.session_state.owner.add_pet(st.session_state.pet)

if "original_minutes" not in st.session_state:
    st.session_state.original_minutes = st.session_state.owner.available_minutes

# Convenience aliases
owner: Owner = st.session_state.owner
pet: Pet = st.session_state.pet

# ---------------------------------------------------------------------------
# Owner & Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
    owner.available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=owner.available_minutes
    )
with col2:
    pet.name = st.text_input("Pet name", value=pet.name)
    pet.species = st.selectbox(
        "Species",
        ["dog", "cat", "other"],
        index=["dog", "cat", "other"].index(pet.species) if pet.species in ["dog", "cat", "other"] else 2,
    )

st.caption(f"Caring for: **{pet.name}** the {pet.species}  |  Owner: **{owner.name}**  |  Time budget: {owner.available_minutes} min")

st.divider()

# ---------------------------------------------------------------------------
# Add tasks — creates real Task objects and attaches them to the Pet
# ---------------------------------------------------------------------------

st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    recurrence_choice = st.selectbox(
        "Recurrence", ["none", "daily", "weekly", "weekdays"]
    )
with col5:
    earliest = st.text_input("Earliest start (HH:MM, optional)", value="")
    latest = st.text_input("Latest end (HH:MM, optional)", value="")

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        task_type="manual",
        required=True,
        earliest_start=earliest.strip() or None,
        latest_end=latest.strip() or None,
        recurrence=None if recurrence_choice == "none" else recurrence_choice,
    )
    pet.add_task(new_task)
    st.success(f"Added: {task_title} ({duration} min, {priority} priority"
               + (f", recurs {recurrence_choice}" if recurrence_choice != "none" else "") + ")")

st.divider()

# ---------------------------------------------------------------------------
# Task list — filter by pet / status, mark complete, sort by time
# ---------------------------------------------------------------------------

st.subheader("Tasks")

pet_names = [p.name for p in owner.pets]
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
with col_f2:
    filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
with col_f3:
    sort_by_time = st.checkbox("Sort by earliest start time")

# Build task list from all pets so filtering works across multiple pets
all_tasks = owner.all_tasks()

# Apply filters
scheduler_for_filter = Scheduler(owner=owner)
filtered_tasks = scheduler_for_filter.filter_tasks(
    all_tasks,
    pet_name=filter_pet if filter_pet != "All" else None,
    completed={"Pending": False, "Completed": True}.get(filter_status),
)

# Optionally sort by time
if sort_by_time:
    filtered_tasks = scheduler_for_filter.sort_tasks_by_time(filtered_tasks)

if filtered_tasks:
    st.write(f"Showing **{len(filtered_tasks)}** task(s):")
    for i, task in enumerate(filtered_tasks):
        col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3, 2, 2, 2, 2, 1])
        with col_a:
            st.write(task.title)
        with col_b:
            st.write(f"{task.duration_minutes} min")
        with col_c:
            st.write(task.priority)
        with col_d:
            st.write(task.pet_name or "—")
        with col_e:
            st.write(task.recurrence or "once")
        with col_f:
            done = st.checkbox(
                "Done",
                value=task.completed,
                key=f"done_{task.title}_{i}",
                label_visibility="collapsed",
            )
            if done and not task.completed:
                task.mark_complete()
            elif not done and task.completed:
                task.completed = False
else:
    st.info("No tasks match the current filter — add one above or adjust the filter.")

# ---------------------------------------------------------------------------
# Recurring tasks summary
# ---------------------------------------------------------------------------

recurring = scheduler_for_filter.recurring_tasks()
if recurring:
    with st.expander(f"Recurring tasks ({len(recurring)})"):
        for t in recurring:
            st.write(f"- **{t.title}** — {t.recurrence} ({t.duration_minutes} min, {t.priority})")

st.divider()

# ---------------------------------------------------------------------------
# Conflict detection — shown before scheduling so owners can fix issues
# ---------------------------------------------------------------------------

conflicts = scheduler_for_filter.detect_conflicts()
if conflicts:
    st.subheader("Time Window Conflicts")
    for a, b in conflicts:
        st.warning(
            f"**{a.title}** ({a.earliest_start}–{a.latest_end}) overlaps with "
            f"**{b.title}** ({b.earliest_start}–{b.latest_end})"
        )
    st.divider()

# ---------------------------------------------------------------------------
# Generate schedule — runs Scheduler and displays explain_plan() output
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Reset available_minutes so the scheduler works from the full budget
        owner.available_minutes = st.session_state.original_minutes
        scheduler = Scheduler(owner=owner)
        schedule = scheduler.generate_schedule()

        if schedule:
            st.success("Schedule generated!")
            st.text(scheduler.explain_plan(schedule))
        else:
            st.warning("No tasks could be scheduled. Try increasing available minutes or reducing task durations.")

# Keep original_minutes in sync when the user changes the time budget
st.session_state.original_minutes = owner.available_minutes
