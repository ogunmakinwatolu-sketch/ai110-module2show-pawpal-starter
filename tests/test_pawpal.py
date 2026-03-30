from pawpal_system import Pet, Task


def make_task():
    return Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        task_type="exercise",
        required=True,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=4)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
