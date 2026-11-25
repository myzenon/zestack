# zestack

A personal AI coding harness that plugs into any project. The AI codes alongside the developer, who stays in control of and understands every change. See `CLAUDE.md`.

## Later

- Worktree support in the Work system (per repo, not per project, since a monorepo's projects share one repo; branch check before code edits).
- Review design, maybe as a review skill. Includes `work-ledger`'s file-by-file checklist idea: write the exact-path checklist into the Task first, and check an item only after the human accepts it. Also pstack's `skills/blast-radius`: find what a change breaks outside the diff, and prove the one fact it's safe because of by running real code.
- A `correct` skill, from pstack's `skills/correct`: find mistakes the AI keeps repeating in a repo and make them impossible, fixing at the highest level that works (architecture, types, lint or CI, test, written rule last).
- Maybe an "understanding" skill, from pstack's `skills/how` (how X works), `skills/why` (why X is this way, cited), and `skills/teach` (both, woven into one plain explanation), to help the human reach the same context.
- Clearing each Work's `tmp/` (for example, when the Work is closed).
- A name for self-sync mode.
- Setting up a second machine in self-sync mode (the `.zestack` symlink, any per-machine settings), since installation covers only the first machine.
- Extendable zestack: add specific skills to a project, like pstack does (and like the current harness's `skill-set.yaml`).
- Agent switching, for example `AGENTS.md` for Codex.
- Statecharts and TLA+ checks (as in pstack) for tricky flows: agree on rules in phase 1, verify risky logic in phase 3.
- Per-project phase: projects in one root can be in different phases (for example a `Phase:` line in each `project.md` instead of one `phase.json`). Open: how a Work that touches two projects in different phases behaves.
