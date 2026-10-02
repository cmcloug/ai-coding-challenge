"""TaskBoard: a tiny in-memory task tracker.

THE SPEC (this is how the code is supposed to behave)
-----------------------------------------------------
- Priority is an int from 1 to 5. 1 is the HIGHEST priority, 5 is the lowest.
- Status is either "open" or "done". New tasks start as "open".
- Due dates are datetime.date objects, or None if the task has no due date.
- A task is OVERDUE if it is still open AND its due date is strictly before
  today. A task due today is NOT overdue. Completed tasks are never overdue.
- Each task owns its own list of tags. Changing one task's tags must never
  affect another task, and must never affect a list the caller passed in.
"""

from datetime import date

VALID_STATUSES = ("open", "done")


class TaskBoard:
    """Stores tasks in memory. Each task is a plain dict."""

    def __init__(self):
        self._tasks = []
        self._next_id = 1

    # ------------------------------------------------------------------
    # Existing functionality
    # ------------------------------------------------------------------
    def add_task(self, title, priority=3, due=None, tags=[]):
        """Create a task and return it."""
        if not title or not title.strip():
            raise ValueError("title is required")
        if priority not in range(1, 6):
            raise ValueError("priority must be between 1 and 5")

        task = {
            "id": self._next_id,
            "title": title.strip(),
            "priority": priority,
            "due": due,
            "tags": tags,
            "status": "open",
        }
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_task(self, task_id):
        """Return the task with this id, or raise KeyError."""
        for task in self._tasks:
            if task["id"] == task_id:
                return task
        raise KeyError(f"no task with id {task_id}")

    def complete_task(self, task_id):
        """Mark a task as done and return it."""
        task = self.get_task(task_id)
        task["status"] = "done"
        return task

    def list_tasks(self, status=None):
        """Return all tasks, or only tasks with the given status."""
        if status is None:
            return list(self._tasks)
        if status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return [t for t in self._tasks if t["status"] != status]

    def sorted_by_priority(self):
        """Return tasks ordered from highest priority (1) to lowest (5).

        Tasks with the same priority keep the order they were added in.
        """
        return sorted(self._tasks, key=lambda t: t["priority"], reverse=True)

    def overdue_tasks(self, today=None):
        """Return the tasks that are overdue (see the spec at the top)."""
        today = today or date.today()
        return [
            t for t in self._tasks
            if t["due"] is not None and t["due"] <= today
        ]

    # ------------------------------------------------------------------
    # FEATURE REQUEST: implement these two methods
    # ------------------------------------------------------------------
    def tasks_by_tag(self, tag):
        """Return all tasks that have the given tag.

        - Matching is case-insensitive ("Urgent" matches "urgent").
        - Ignore leading/trailing spaces in the tag you are searching for.
        - Return tasks in the order they were added.
        - If nothing matches, return an empty list.
        """
        raise NotImplementedError("TODO: implement tasks_by_tag")

    def summary(self, today=None):
        """Return a dict of counts describing the board.

        Keys: "total", "open", "done", "overdue".
        "overdue" follows the same rule as overdue_tasks().
        """
        raise NotImplementedError("TODO: implement summary")
