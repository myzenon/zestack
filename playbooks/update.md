# Update

How the AI updates a project's `.zestack/core/` to the latest zestack. The human starts it by asking the AI to update zestack using this file's GitHub URL. Read it from GitHub, not from `.zestack/core/`, because the installed copy may be older than the steps it needs.

`.zestack/state/` is never touched by an update. It holds the project's decisions and Works, which belong to the project, not to zestack.

## Steps

1. **Find the mode.** In the root (the folder that holds `.zestack/`): if `.zestack` is a symlink, it's self-sync mode. Otherwise it's git mode.
2. **Show what changed.** Clone the latest zestack to a temp folder (SSH by default, HTTPS if SSH fails, as in installation). Compare the hash in `.zestack/core/VERSION` with the clone's `HEAD`, and show the human the zestack commits in between (`git -C <temp> log --oneline <installed>..HEAD`). If they're the same, tell the human it's already up to date and stop.
3. **Ask.** Wait for the human's OK before changing anything, because an update changes how the AI behaves in this project.
4. **Update `core/`.** First check whether `core/` was edited in the project: check out `<installed>` in the temp clone and diff it against `core/`, ignoring `VERSION` and `.git/`. Then check out `main` again. If `core/` was edited, stop and show the human, because `core/` shouldn't be edited in a project, and the changes may be a mistake or something worth moving into zestack itself. Otherwise replace `.zestack/core/` with the temp clone, without its `.git/`, and write the clone's hash to `.zestack/core/VERSION`. In git mode, the human reviews the change as a diff in the project repo.
5. **Re-link the skills.** For each skill folder in `.zestack/core/skills/`, make sure `<root>/.claude/skills/<skill>` links to it, as in installation. Remove links in `.claude/skills/` that point into `.zestack/core/` but no longer resolve, because a removed or renamed skill leaves its old link broken. In self-sync mode, keep `.git/info/exclude` matching the links.
6. **State changes.** If the new zestack expects something different in `.zestack/state/` (a new file, a renamed one), tell the human what and why, and change it only after their OK. Known so far: `notes/` (added after the first release) needs no migration, because it's created when the first note is written. `projects/<project>/project.md` (added after the first release) is needed for every existing project: propose each one's `Path:` and `What it is:` from the code, and write them after the human's OK.
7. **Check.** If `CLAUDE.md` or the skills changed, ask the human to start a new session and run `/memory` and `/skills`.
