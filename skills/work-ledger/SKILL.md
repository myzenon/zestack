---
name: work-ledger
description: Records zestack Works and Tasks in .zestack/state/work/ so work survives the end of a session, a context summary, and a switch of machine. Use for all work in a zestack project, including when the human asks to start new work or continue or resume work, even without a Work ID.
---

# Work ledger

A Work is one piece of work the human wants done, such as a feature or a fix. It can touch one project or several. A Task is one part of a Work inside one project. Everything is written to files, because session context is lost and the files are what the next session reads.

## Start and resume

Arguments: `$ARGUMENTS`

- `new`: create a new Work with the human (see Create a Work).
- `continue`, or no argument and no Work established in this session: run the tool's list of open Works, show the short result, and ask the human to pick one ID or `new`. Read no Work until the human chooses, so you never guess which Work they mean.
- Show IDs as a short prefix, like a git commit. The tool resolves a prefix and refuses an ambiguous one; never complete an ID yourself.

## Files

```text
.zestack/state/work/<id>/
├── work.md              shared by every project in the Work
├── handoff.md           events between projects (only when used)
├── tmp/                 this Work's scratch files
└── <project>/
    ├── work.md          this project's part
    └── task-<id>.md     a Task that grew past ~15 lines
```

A folder named `paused-<id>` is paused, `completed-<id>` is done, and a plain `<id>` is active.

**Top `work.md`** holds only what every project shares:
- Outcome: the intended finished result
- Approach: the agreed direction across projects, including agreements between projects such as an API spec
- Verification: the final check that it's done
- Later: postponed topics, one line each

**`<project>/work.md`** holds this project's part: Outcome, Work context (relevant paths, each with a short reason), Approach, Current task, Tasks (one line per Task), Done when, and Verification. Add Key decisions, Project state, Blocked on, or Pending human action only when needed.

## Tool

The tool owns IDs, folder renames, and locking, so those stay exact. Never edit them by hand. You write the prose (Outcome, Approach, notes) directly in the files.

Commands: TODO, designed with `scripts/work.py`.

## Tasks

- New work goes into the Current task. When new work doesn't fit it, tell the human and suggest a new Task. Create a Task only after the human agrees, because a split the human didn't choose makes the Work harder to follow.
- Each Task has a `Focus:` line directly under its title: what is being done right now in that Task. Switching Tasks keeps each Task's place.
- A Task's notes stay inline in `work.md` while short. Past about 15 lines, move them to `task-<id>.md` and keep a one-line pointer in `work.md`, so `work.md` stays quick to read.
- Each log line is a pointer plus one short why, never a retelling, because git already holds the story:

  ```text
  4f15f09 — fixed login lock race
  ```

## Focus and the later list

Follow the one-focus principle in `CLAUDE.md`. In the Work:
- Keep the current Task's `Focus:` line current: update it when the human says OK to a switch, so a new session continues on the same topic.
- When a new topic comes up, write it as one line under Later instead of discussing it.
- When the current Focus is done, bring up Later before anything new, and let the human pick the next item or drop one.

## Keeping files current

- When a new decision changes an earlier one, delete the old text in the same write. No "superseded" or "kept as history" notes, because stale text misleads the next session. Git holds the history.
- Work and Task files are durable. Never delete, truncate, or recreate them to reorganize. If a fix would delete a Task, a Work file, or content that's still current, show the human the exact change and wait for their OK. Replacing an old decision is normal upkeep and doesn't need this.

## Between projects

`handoff.md` is for events, one line per round, for example `api: the new endpoint is ready, web can use it`. An agreement that stays true for the whole Work, such as an API spec, goes in the top `work.md` under Approach, so it isn't buried in a log.

## Scratch

Put this Work's scratch files only in its `tmp/`, so they don't spread across the project.

## PRs

A PR or branch recorded by a Work stays owned by that Work. Review comments, failed checks, and follow-up fixes become a new Task in the same Work, suggested and created as in Tasks above. If the Work is already closed, ask the human before reopening it.

## Pause and close

Only the human pauses, resumes, or closes a Work. Finished Tasks, passing tests, or a merged PR are evidence, not permission. Run the tool command only after the human says so for that Work.
