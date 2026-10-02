"""Tests for taskboard.py

Run from this folder with:
    python -m unittest -v

No packages to install. Everything uses the Python standard library.
"""

import unittest
from datetime import date

from taskboard import TaskBoard

TODAY = date(2025, 6, 15)


class TestBasics(unittest.TestCase):
    def setUp(self):
        self.board = TaskBoard()

    def test_add_task_assigns_incrementing_ids(self):
        a = self.board.add_task("First")
        b = self.board.add_task("Second")
        self.assertEqual((a["id"], b["id"]), (1, 2))

    def test_add_task_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            self.board.add_task("   ")

    def test_add_task_rejects_bad_priority(self):
        with self.assertRaises(ValueError):
            self.board.add_task("Bad", priority=9)

    def test_complete_task(self):
        t = self.board.add_task("Ship it")
        self.board.complete_task(t["id"])
        self.assertEqual(self.board.get_task(t["id"])["status"], "done")

    def test_get_missing_task_raises(self):
        with self.assertRaises(KeyError):
            self.board.get_task(42)


class TestListing(unittest.TestCase):
    def setUp(self):
        self.board = TaskBoard()
        self.t1 = self.board.add_task("One")
        self.t2 = self.board.add_task("Two")
        self.t3 = self.board.add_task("Three")
        self.board.complete_task(self.t2["id"])

    def test_list_all(self):
        self.assertEqual(len(self.board.list_tasks()), 3)

    def test_list_open_only(self):
        titles = [t["title"] for t in self.board.list_tasks("open")]
        self.assertEqual(titles, ["One", "Three"])

    def test_list_done_only(self):
        titles = [t["title"] for t in self.board.list_tasks("done")]
        self.assertEqual(titles, ["Two"])

    def test_list_invalid_status_raises(self):
        with self.assertRaises(ValueError):
            self.board.list_tasks("archived")


class TestSorting(unittest.TestCase):
    def test_priority_one_comes_first_and_ties_keep_order(self):
        board = TaskBoard()
        board.add_task("C", priority=3)
        board.add_task("A", priority=1)
        board.add_task("B", priority=2)
        board.add_task("A2", priority=1)
        titles = [t["title"] for t in board.sorted_by_priority()]
        self.assertEqual(titles, ["A", "A2", "B", "C"])


class TestOverdue(unittest.TestCase):
    def setUp(self):
        self.board = TaskBoard()

    def test_past_due_open_task_is_overdue(self):
        self.board.add_task("Late", due=date(2025, 6, 1))
        self.assertEqual(len(self.board.overdue_tasks(today=TODAY)), 1)

    def test_task_due_today_is_not_overdue(self):
        self.board.add_task("Due today", due=TODAY)
        self.assertEqual(self.board.overdue_tasks(today=TODAY), [])

    def test_completed_task_is_never_overdue(self):
        t = self.board.add_task("Done late", due=date(2025, 6, 1))
        self.board.complete_task(t["id"])
        self.assertEqual(self.board.overdue_tasks(today=TODAY), [])

    def test_task_without_due_date_is_not_overdue(self):
        self.board.add_task("Whenever")
        self.assertEqual(self.board.overdue_tasks(today=TODAY), [])


class TestTagIsolation(unittest.TestCase):
    def test_tasks_do_not_share_default_tags(self):
        board = TaskBoard()
        a = board.add_task("A")
        a["tags"].append("urgent")
        b = board.add_task("B")
        self.assertEqual(b["tags"], [])

    def test_task_does_not_share_list_with_caller(self):
        board = TaskBoard()
        my_tags = ["home"]
        board.add_task("A", tags=my_tags)
        my_tags.append("changed-later")
        self.assertEqual(board.get_task(1)["tags"], ["home"])


class TestFeatureTasksByTag(unittest.TestCase):
    def setUp(self):
        self.board = TaskBoard()
        self.board.add_task("A", tags=["Urgent", "work"])
        self.board.add_task("B", tags=["home"])
        self.board.add_task("C", tags=["URGENT"])

    def test_case_insensitive_match_in_added_order(self):
        titles = [t["title"] for t in self.board.tasks_by_tag("urgent")]
        self.assertEqual(titles, ["A", "C"])

    def test_search_term_is_trimmed(self):
        titles = [t["title"] for t in self.board.tasks_by_tag("  home ")]
        self.assertEqual(titles, ["B"])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(self.board.tasks_by_tag("nope"), [])


class TestFeatureSummary(unittest.TestCase):
    def test_summary_counts(self):
        board = TaskBoard()
        board.add_task("Late", due=date(2025, 6, 1))
        board.add_task("Due today", due=TODAY)
        done = board.add_task("Finished", due=date(2025, 6, 2))
        board.complete_task(done["id"])
        board.add_task("No date")
        self.assertEqual(
            board.summary(today=TODAY),
            {"total": 4, "open": 3, "done": 1, "overdue": 1},
        )

    def test_summary_empty_board(self):
        self.assertEqual(
            TaskBoard().summary(today=TODAY),
            {"total": 0, "open": 0, "done": 0, "overdue": 0},
        )


if __name__ == "__main__":
    unittest.main()
