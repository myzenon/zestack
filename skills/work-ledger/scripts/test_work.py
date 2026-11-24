"""Tests for work.py. Run: python3 -m unittest test_work (from this folder)."""
from __future__ import annotations

import contextlib
import io
import os
import re
import tempfile
import unittest
from pathlib import Path

import work


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".zestack" / "state").mkdir(parents=True)
        self._cwd = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def run_tool(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = work.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def new_work(self, *projects: str) -> str:
        code, out, _ = self.run_tool("work", "new", "--outcome", "Add Google login", "--projects", *projects)
        self.assertEqual(code, 0)
        return re.search(r"Created Work ([0-9a-f-]+)\.", out).group(1)

    def work_dir(self) -> Path:
        return self.root / ".zestack" / "state" / "work"


class IdTest(unittest.TestCase):
    def test_uuid7_shape(self):
        value = work.uuid7()
        self.assertRegex(value, r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")

    def test_uuid7_is_time_ordered(self):
        first = work.uuid7()
        import time
        time.sleep(0.002)
        self.assertLess(first, work.uuid7())

    def test_short_ids_extend_when_shared(self):
        ids = ["0190aaaa-1111-7000-8000-000000000000", "0190aaaa-2222-7000-8000-000000000000"]
        shorts = work.short_ids(ids)
        self.assertEqual(shorts[ids[0]], "0190aaaa-1")
        self.assertEqual(shorts[ids[1]], "0190aaaa-2")


class WorkCommandsTest(LedgerTest):
    def test_new_creates_files(self):
        short = self.new_work("api", "web")
        folders = list(self.work_dir().iterdir())
        self.assertEqual(len(folders), 1)
        self.assertTrue(folders[0].name.startswith(short))
        top = (folders[0] / "work.md").read_text()
        self.assertIn("## Later", top)
        self.assertIn("Add Google login", top)
        self.assertIn("Current task: none", (folders[0] / "api" / "work.md").read_text())
        self.assertTrue((folders[0] / "web" / "work.md").exists())

    def test_list_shows_open_works_only(self):
        short = self.new_work("api")
        _, out, _ = self.run_tool("work", "list")
        self.assertIn(short, out)
        self.assertIn("Add Google login", out)
        self.assertIn("[api]", out)
        self.run_tool("work", "close", short)
        _, out, _ = self.run_tool("work", "list")
        self.assertIn("No open Works.", out)
        _, out, _ = self.run_tool("work", "list", "--all")
        self.assertIn("completed", out)

    def test_pause_resume_close_rename_folder(self):
        short = self.new_work("api")
        self.run_tool("work", "pause", short)
        self.assertTrue(next(self.work_dir().iterdir()).name.startswith("paused-"))
        self.run_tool("work", "resume", short)
        self.assertTrue(next(self.work_dir().iterdir()).name.startswith(short))
        self.run_tool("work", "close", short)
        self.assertTrue(next(self.work_dir().iterdir()).name.startswith("completed-"))

    def test_same_status_is_refused(self):
        short = self.new_work("api")
        code, _, err = self.run_tool("work", "resume", short)
        self.assertEqual(code, 1)
        self.assertIn("already active", err)

    def test_path_and_add_project(self):
        short = self.new_work("api")
        _, out, _ = self.run_tool("work", "add-project", short, "web")
        self.assertTrue(Path(out.splitlines()[-1]).exists())
        _, out, _ = self.run_tool("work", "path", short, "web")
        self.assertTrue(out.strip().endswith("web/work.md"))
        code, _, err = self.run_tool("work", "path", short, "nope")
        self.assertEqual(code, 1)
        self.assertIn("Projects: api, web", err)

    def test_tmp_is_not_a_project(self):
        short = self.new_work("api")
        self.run_tool("work", "tmp", short)
        _, out, _ = self.run_tool("work", "list")
        self.assertIn("[api]", out)

    def test_unknown_and_ambiguous_prefix(self):
        self.new_work("api")
        self.new_work("api")
        code, _, err = self.run_tool("work", "path", "ffff")
        self.assertEqual(code, 1)
        self.assertIn("No Work matches", err)
        prefix = next(self.work_dir().iterdir()).name[:4]
        code, _, err = self.run_tool("work", "path", prefix)
        self.assertEqual(code, 1)
        self.assertIn("several Works", err)

    def test_no_state_folder(self):
        os.chdir(tempfile.gettempdir())
        code, _, err = self.run_tool("work", "list")
        self.assertEqual(code, 1)
        self.assertIn("No .zestack/state/", err)

    def test_finds_state_from_subfolder(self):
        sub = self.root / "repo" / "src"
        sub.mkdir(parents=True)
        os.chdir(sub)
        self.new_work("api")
        self.assertEqual(len(list(self.work_dir().iterdir())), 1)


class TaskCommandsTest(LedgerTest):
    def add_task(self, short: str, title: str) -> None:
        code, _, _ = self.run_tool("task", "add", short, "api", "--title", title)
        self.assertEqual(code, 0)

    def task_ids(self) -> list[str]:
        """Full Task IDs in order. A short ID printed at creation can become
        ambiguous once a later Task shares its timestamp prefix."""
        return [t[0] for t in work.tasks_in(self.project_md().read_text())]

    def project_md(self) -> Path:
        return next(self.work_dir().iterdir()) / "api" / "work.md"

    def test_add_goes_into_tasks_section(self):
        short = self.new_work("api")
        self.add_task(short, "OAuth callback")
        text = self.project_md().read_text()
        tasks = work.section(text, "Tasks")
        self.assertIn("— OAuth callback", tasks)
        self.assertIn("Focus: none", tasks)
        self.assertIn("## Done when", text)

    def test_current_and_list(self):
        short = self.new_work("api")
        self.add_task(short, "OAuth callback")
        self.add_task(short, "Session timeout")
        task = self.task_ids()[0]
        self.assertEqual(self.run_tool("task", "current", short, "api", task)[0], 0)
        self.assertIn(f"Current task: `{task}", self.project_md().read_text())
        _, out, _ = self.run_tool("task", "list", short, "api")
        lines = out.splitlines()
        self.assertIn("* OAuth callback", lines[0])
        self.assertNotIn("*", lines[1])
        self.run_tool("task", "current", short, "api", "none")
        self.assertIn("Current task: none", self.project_md().read_text())

    def test_done(self):
        short = self.new_work("api")
        self.add_task(short, "OAuth callback")
        task = self.task_ids()[0]
        self.run_tool("task", "done", short, "api", task)
        self.assertIn("— done — OAuth callback", self.project_md().read_text())
        _, out, _ = self.run_tool("task", "list", short, "api")
        self.assertIn("done", out)
        code, _, err = self.run_tool("task", "done", short, "api", task)
        self.assertEqual(code, 1)
        self.assertIn("already done", err)

    def test_spill_moves_notes_and_keeps_focus(self):
        short = self.new_work("api")
        self.add_task(short, "OAuth callback")
        self.add_task(short, "Session timeout")
        task = self.task_ids()[0]
        path = self.project_md()
        text = path.read_text().replace("Focus: none", "Focus: validate state\n- note one\n- note two", 1)
        path.write_text(text)
        _, out, _ = self.run_tool("task", "spill", short, "api", task)
        spill = Path(out.split("Spilled to ")[1].strip())
        self.assertIn("- note one", spill.read_text())
        after = path.read_text()
        self.assertNotIn("- note one", after)
        self.assertIn("Focus: validate state", after)
        self.assertIn(f"Notes: task-", after)
        self.assertIn("— Session timeout", after)
        code, _, err = self.run_tool("task", "spill", short, "api", task)
        self.assertEqual(code, 1)
        self.assertIn("already spilled", err)


if __name__ == "__main__":
    unittest.main()
