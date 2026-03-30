# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Four algorithmic improvements were added to make the scheduler more useful for real pet-owner workflows:

### Sort by time
`Scheduler.sort_tasks_by_time(tasks)` orders any task list chronologically by `earliest_start`. Tasks without a time window sink to the end of the list. A lambda key function converts each `HH:MM` string into a comparable `datetime` object so the sort is accurate even across midnight boundaries.

### Filter by pet or status
`Scheduler.filter_tasks(tasks, pet_name, completed)` narrows a task list to exactly what the owner needs to see. Filters can be used independently or combined — e.g., "show only Luna's pending tasks." Pet matching uses object identity rather than string comparison, so two pets with similar task names are never confused.

### Recurring tasks
Tasks accept a `recurrence` field (`"daily"`, `"weekly"`, or `"weekdays"`). When a recurring task is completed, `Scheduler.complete_and_reschedule(task)` automatically creates the next occurrence and attaches it to the correct pet. Next dates are calculated with Python's `timedelta`: daily adds 1 day, weekly adds 7, and weekdays advances to the next Mon–Fri, skipping Saturday and Sunday.

### Conflict detection
`Scheduler.detect_conflicts()` scans all tasks with defined time windows and flags any pair whose windows overlap using the condition `a_start < b_end AND b_start < a_end`. `Scheduler.conflict_warnings()` wraps the raw pairs into plain-English strings that identify whether the clash is within the same pet or across different pets. Warnings are printed automatically at the start of `generate_schedule()` — the schedule is still produced, so no task is silently dropped.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
