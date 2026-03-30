# PawPal+ Project Reflection

## 1. System Design
Three core actions a user can perform:
- Setup tasks/routine for care per pet registered.
- Add/register pet.
- View daily schedule/plan.

**a. Initial design**

- Briefly describe your initial UML design.
**Answer:**
The design models a pet care scheduling system with four classes:

Pet — holds the animal's profile (species, age, special_needs, daily_needs) and exposes methods to check its care requirements. It drives what tasks need to exist.

Task — a dataclass representing a single care activity (feeding, medication, walks, etc.) with timing constraints and priority. Tasks originate from a Pet's needs.

Owner — tracks the person's time availability and time-of-day preferences. They use the Scheduler and ultimately perform the tasks.

Scheduler — the coordinator. It takes an Owner, Pet, and list of Tasks as inputs, then selects, orders, and allocates tasks into a feasible schedule based on the owner's availability.

The flow:

Pet's needs → Tasks → Scheduler organizes them → Owner performs them

The key design decision is that Scheduler doesn't own the domain objects — it receives them from outside, keeping the classes loosely coupled and independently testable.


- What classes did you include, and what responsibilities did you assign to each?
**Answer:** 
Owner
Manages the person's time and preferences. Responsible for tracking available minutes, time-of-day preferences, and consuming time as tasks are assigned.

Pet
Represents the animal's profile and care needs. Responsible for surfacing whether it needs medication, extra care, and producing a summary of its needs.

Task
Represents a single schedulable care activity. Responsible for knowing its own priority, whether it fits within a time window, and whether it can be scheduled given available time.

Scheduler
The coordinator of the whole system. Responsible for selecting which tasks to run, ordering them by priority, allocating them against the owner's available time, and producing a human-readable explanation of the plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**Answer:**
Yes, five changes were made after reviewing the class skeleton against the UML:

1. **Added `Pet.generate_tasks()`** — The UML specifies a `Pet --> Task : requires` relationship but the skeleton had no code connecting them. This method was added so tasks originate from `daily_needs` and `special_needs` rather than always being created externally.

2. **Guarded `Owner.use_minutes()` against overdraft** — `use_minutes()` could be called without first checking `is_available()`, allowing `available_minutes` to go negative. A `ValueError` is now raised if the requested duration exceeds what remains.

3. **Enforced a consistent time format (`TIME_FORMAT = "%H:%M"`)** — `earliest_start`, `latest_end`, and `available_windows` all used raw strings with no enforced format. A module-level constant and a `Task._parse_time()` helper were added so all time comparisons use the same format and bad input fails fast.

4. **Kept `Task.is_required()` with a clarifying docstring** — The method is a wrapper around `self.required`, but it was retained for polymorphic access and documented so the intent is clear.

5. **Added `Scheduler.validate_schedule()`** — No method existed to verify a completed schedule stays within the owner's `available_minutes`. This method is called after `allocate_time()` and before the final schedule is returned.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
