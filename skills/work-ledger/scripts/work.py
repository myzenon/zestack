#!/usr/bin/env python3
"""zestack Work ledger tool.

Does the exact parts of the Work system: IDs, the files it creates, folder
renames, and locking. Everything else in work.md is prose the AI edits directly.

Standard library only, Python 3.9+, macOS and Linux (WSL).
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import os
import re
import secrets
import sys
import tempfile
import time
from pathlib import Path

# 8 hex characters, like a short git commit. Extended when two IDs share it:
# a UUIDv7 starts with its timestamp, so IDs made within about a minute of
# each other share their first 8 characters.
SHORT_ID_MIN = 8

PAUSED = "paused-"
COMPLETED = "completed-"

TASK_HEADING = re.compile(r"^### `([0-9a-f-]{36})` — (?:(done) — )?(.*)$")
CURRENT_TASK = re.compile(r"^Current task: .*$", re.MULTILINE)


class ToolError(Exception):
    """An error the AI can act on. Printed without a traceback."""


# ---------- IDs ----------

def uuid7() -> str:
    """Build a UUIDv7 (RFC 9562). Python's uuid module has uuid7() only from 3.14."""
    ms = time.time_ns() // 1_000_000
    value = (ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76                      # version 7
    value |= secrets.randbits(12) << 64
    value |= 0b10 << 62                     # RFC 9562 variant
    value |= secrets.randbits(62)
    h = f"{value:032x}"
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"


def short_ids(ids: list[str]) -> dict[str, str]:
    """Shortest prefix of each ID (at least SHORT_ID_MIN) that no other ID shares."""
    result = {}
    for full in ids:
        n = SHORT_ID_MIN
        while any(o != full and o.startswith(full[:n]) for o in ids):
            n += 1
        result[full] = full[:n]
    return result


def resolve(prefix: str, ids: list[str], kind: str) -> str:
    matches = [i for i in ids if i.startswith(prefix.lower())]
    if not matches:
        raise ToolError(f"No {kind} matches '{prefix}'.")
    if len(matches) > 1:
        shown = ", ".join(sorted(short_ids(ids)[m] for m in matches))
        raise ToolError(f"'{prefix}' matches several {kind}s: {shown}. Give a longer prefix.")
    return matches[0]


# ---------- Locating state ----------

def state_dir() -> Path:
    """Find .zestack/state/ in the current folder or the nearest parent."""
    here = Path.cwd().resolve()
    for folder in [here, *here.parents]:
        candidate = folder / ".zestack" / "state"
        if candidate.is_dir():
            return candidate
    raise ToolError("No .zestack/state/ found in this folder or any parent. Is zestack installed here?")


def work_root() -> Path:
    root = state_dir() / "work"
    root.mkdir(exist_ok=True)
    return root


@contextlib.contextmanager
def locked():
    """Lock the ledger while a command runs, so two sessions can't overwrite each other.

    The lock file lives in the system temp folder, not in .zestack/, so it never
    reaches git or sync. Locks are per machine.
    """
    key = hashlib.sha256(str(state_dir()).encode()).hexdigest()[:16]
    path = Path(tempfile.gettempdir()) / f"zestack-work-{key}.lock"
    with open(path, "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


# ---------- Works ----------

def split_status(name: str) -> tuple[str, str]:
    """Folder name → (status, full id)."""
    if name.startswith(PAUSED):
        return "paused", name[len(PAUSED):]
    if name.startswith(COMPLETED):
        return "completed", name[len(COMPLETED):]
    return "active", name


def all_works() -> dict[str, tuple[str, Path]]:
    """Full id → (status, folder)."""
    works = {}
    for folder in sorted(work_root().iterdir()):
        if folder.is_dir():
            status, full = split_status(folder.name)
            works[full] = (status, folder)
    return works


def find_work(prefix: str) -> tuple[str, str, Path]:
    works = all_works()
    full = resolve(prefix, list(works), "Work")
    status, folder = works[full]
    return full, status, folder


def section(text: str, name: str) -> str:
    """Body of a '## name' section, without the heading."""
    match = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def top_template(outcome: str) -> str:
    return (
        f"## Outcome\n\n{outcome}\n\n"
        "## Approach\n\nPending.\n\n"
        "## Verification\n\nPending.\n\n"
        "## Later\n\n- None.\n"
    )


def project_template() -> str:
    return (
        "Current task: none\n\n"
        "## Outcome\n\nPending.\n\n"
        "## Work context\n\n- None yet.\n\n"
        "## Approach\n\nPending.\n\n"
        "## Tasks\n\n"
        "## Done when\n\nPending.\n\n"
        "## Verification\n\nPending.\n"
    )


def check_project_name(name: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) or name == "tmp":
        raise ToolError(f"'{name}' is not a usable project name. Use letters, digits, '.', '_', '-' (not 'tmp').")


def cmd_work_new(args) -> None:
    for project in args.projects:
        check_project_name(project)
    full = uuid7()
    folder = work_root() / full
    folder.mkdir()
    (folder / "work.md").write_text(top_template(args.outcome))
    print(f"Created Work {short_ids(list(all_works()))[full]}.")
    print(folder / "work.md")
    for project in args.projects:
        (folder / project).mkdir()
        (folder / project / "work.md").write_text(project_template())
        print(folder / project / "work.md")


def projects_of(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.iterdir() if p.is_dir() and p.name != "tmp")


def cmd_work_list(args) -> None:
    works = all_works()
    shorts = short_ids(list(works))
    shown = 0
    for full, (status, folder) in works.items():
        if status == "completed" and not args.all:
            continue
        top = folder / "work.md"
        outcome = section(top.read_text(), "Outcome").splitlines() if top.exists() else []
        first = outcome[0] if outcome else "(no outcome)"
        print(f"{shorts[full]}  {status:<9}  {first}  [{', '.join(projects_of(folder))}]")
        shown += 1
    if not shown:
        print("No open Works." if not args.all else "No Works.")


def cmd_work_path(args) -> None:
    _, _, folder = find_work(args.id)
    if args.project:
        path = folder / args.project / "work.md"
        if not path.exists():
            raise ToolError(f"Work has no project '{args.project}'. Projects: {', '.join(projects_of(folder))}.")
        print(path)
    else:
        print(folder / "work.md")


def cmd_work_add_project(args) -> None:
    check_project_name(args.project)
    _, _, folder = find_work(args.id)
    target = folder / args.project
    if target.exists():
        raise ToolError(f"Work already has project '{args.project}'.")
    target.mkdir()
    (target / "work.md").write_text(project_template())
    print(f"Added project '{args.project}'.")
    print(target / "work.md")


def rename_work(prefix: str, new_status: str) -> None:
    full, status, folder = find_work(prefix)
    if status == new_status:
        raise ToolError(f"Work is already {status}.")
    names = {"active": full, "paused": PAUSED + full, "completed": COMPLETED + full}
    folder.rename(folder.parent / names[new_status])
    short = short_ids(list(all_works()))[full]
    print(f"Work {short}: {status} → {new_status}.")


def cmd_work_pause(args) -> None:
    rename_work(args.id, "paused")


def cmd_work_resume(args) -> None:
    rename_work(args.id, "active")


def cmd_work_close(args) -> None:
    rename_work(args.id, "completed")


def cmd_work_tmp(args) -> None:
    _, _, folder = find_work(args.id)
    tmp = folder / "tmp"
    tmp.mkdir(exist_ok=True)
    print(tmp)


# ---------- Tasks ----------

def project_file(work_prefix: str, project: str) -> Path:
    _, _, folder = find_work(work_prefix)
    path = folder / project / "work.md"
    if not path.exists():
        raise ToolError(f"Work has no project '{project}'. Projects: {', '.join(projects_of(folder))}.")
    return path


def tasks_in(text: str) -> list[tuple[str, bool, str]]:
    """(full id, done, title) for each Task heading, in order."""
    found = []
    for line in text.splitlines():
        match = TASK_HEADING.match(line)
        if match:
            found.append((match.group(1), match.group(2) == "done", match.group(3)))
    return found


def find_task(text: str, prefix: str) -> str:
    return resolve(prefix, [t[0] for t in tasks_in(text)], "Task")


def task_block(lines: list[str], full: str) -> tuple[int, int]:
    """Line range [start, end) of a Task: its heading up to the next ### or ## heading."""
    start = next(i for i, l in enumerate(lines) if l.startswith(f"### `{full}`"))
    end = start + 1
    while end < len(lines) and not lines[end].startswith(("### ", "## ")):
        end += 1
    return start, end


def cmd_task_add(args) -> None:
    path = project_file(args.id, args.project)
    text = path.read_text()
    lines = text.splitlines()
    if "## Tasks" not in lines:
        raise ToolError(f"{path} has no '## Tasks' section.")
    full = uuid7()
    i = lines.index("## Tasks") + 1
    while i < len(lines) and not lines[i].startswith("## "):
        i += 1
    while i > 0 and lines[i - 1] == "":
        i -= 1
    block = ["", f"### `{full}` — {args.title}", "Focus: none"]
    lines[i:i] = block
    path.write_text("\n".join(lines) + "\n")
    print(f"Added Task {short_ids([t[0] for t in tasks_in(path.read_text())])[full]}.")


def cmd_task_current(args) -> None:
    path = project_file(args.id, args.project)
    text = path.read_text()
    if not CURRENT_TASK.search(text):
        raise ToolError(f"{path} has no 'Current task:' line.")
    if args.task == "none":
        value, shown = "none", "none"
    else:
        full = find_task(text, args.task)
        value, shown = f"`{full}`", short_ids([t[0] for t in tasks_in(text)])[full]
    path.write_text(CURRENT_TASK.sub(f"Current task: {value}", text, count=1))
    print(f"Current task: {shown}.")


def cmd_task_list(args) -> None:
    text = project_file(args.id, args.project).read_text()
    tasks = tasks_in(text)
    if not tasks:
        print("No Tasks.")
        return
    current = CURRENT_TASK.search(text)
    current_id = current.group(0).split("`")[1] if current and "`" in current.group(0) else None
    shorts = short_ids([t[0] for t in tasks])
    for full, done, title in tasks:
        marks = ("done  " if done else "      ") + ("* " if full == current_id else "  ")
        print(f"{shorts[full]}  {marks}{title}")


def cmd_task_spill(args) -> None:
    path = project_file(args.id, args.project)
    lines = path.read_text().splitlines()
    full = find_task("\n".join(lines), args.task)
    start, end = task_block(lines, full)
    body = lines[start + 1:end]
    keep = [l for l in body if l.startswith("Focus: ")]
    notes = [l for l in body if not l.startswith("Focus: ")]
    while notes and notes[-1] == "":
        notes.pop()
    pointer = f"Notes: task-{full}.md"
    if pointer in notes:
        raise ToolError("Task is already spilled.")
    spill = path.parent / f"task-{full}.md"
    spill.write_text(lines[start] + "\n\n" + "\n".join(notes) + "\n")
    lines[start + 1:end] = keep + [pointer, ""]
    path.write_text("\n".join(lines) + "\n")
    print(f"Spilled to {spill}")


def cmd_task_done(args) -> None:
    path = project_file(args.id, args.project)
    lines = path.read_text().splitlines()
    full = find_task("\n".join(lines), args.task)
    start, _ = task_block(lines, full)
    match = TASK_HEADING.match(lines[start])
    if match.group(2) == "done":
        raise ToolError("Task is already done.")
    lines[start] = f"### `{full}` — done — {match.group(3)}"
    path.write_text("\n".join(lines) + "\n")
    print("Task marked done.")


# ---------- CLI ----------

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="work.py", description="zestack Work ledger.")
    groups = p.add_subparsers(dest="group", required=True)

    work = groups.add_parser("work").add_subparsers(dest="command", required=True)
    c = work.add_parser("new", help="create a Work")
    c.add_argument("--outcome", required=True)
    c.add_argument("--projects", nargs="+", required=True)
    c.set_defaults(func=cmd_work_new)
    c = work.add_parser("list", help="list open Works")
    c.add_argument("--all", action="store_true", help="include completed Works")
    c.set_defaults(func=cmd_work_list)
    c = work.add_parser("path", help="print a Work's file path")
    c.add_argument("id")
    c.add_argument("project", nargs="?")
    c.set_defaults(func=cmd_work_path)
    c = work.add_parser("add-project", help="add a project to a Work")
    c.add_argument("id")
    c.add_argument("project")
    c.set_defaults(func=cmd_work_add_project)
    for name, func in (("pause", cmd_work_pause), ("resume", cmd_work_resume),
                       ("close", cmd_work_close), ("tmp", cmd_work_tmp)):
        c = work.add_parser(name)
        c.add_argument("id")
        c.set_defaults(func=func)

    task = groups.add_parser("task").add_subparsers(dest="command", required=True)
    c = task.add_parser("add", help="add a Task")
    c.add_argument("id")
    c.add_argument("project")
    c.add_argument("--title", required=True)
    c.set_defaults(func=cmd_task_add)
    c = task.add_parser("current", help="set the Current task")
    c.add_argument("id")
    c.add_argument("project")
    c.add_argument("task", help="Task ID prefix, or 'none'")
    c.set_defaults(func=cmd_task_current)
    c = task.add_parser("list", help="list a project's Tasks")
    c.add_argument("id")
    c.add_argument("project")
    c.set_defaults(func=cmd_task_list)
    for name, func in (("spill", cmd_task_spill), ("done", cmd_task_done)):
        c = task.add_parser(name)
        c.add_argument("id")
        c.add_argument("project")
        c.add_argument("task")
        c.set_defaults(func=func)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        with locked():
            args.func(args)
    except ToolError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
