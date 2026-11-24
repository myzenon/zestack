# Installation

How the AI installs zestack into a project. The human starts it by asking the AI to install zestack using this file's GitHub URL.

## Steps

1. **Root.** Ask the human which folder is the root: a repo, or a workspace folder that holds several repos. One `.zestack/` serves the whole root, so a wrong root puts it in the wrong place, for example inside one package of a monorepo.
2. **Mode.** Ask the human which mode:
   - **Git mode:** `.zestack/` is committed with the project, so the team can see it.
   - **Self-sync mode:** `.zestack/` stays out of the project's git and syncs through Obsidian, so the harness follows the human across machines without touching the project's repo.
3. **Place `.zestack/`.**
   - Git mode: create `<root>/.zestack/`.
   - Self-sync mode: ask the human for the folder in their Obsidian vault, for example `/obsidian/projecta`. Create it, link `<root>/.zestack -> /obsidian/projecta`, and add `.zestack` to the root repo's `.git/info/exclude`. The real folder lives in the vault, because Obsidian syncs the vault.
4. **Clone.** Clone zestack into `.zestack/core/`. Use SSH by default:

   ```
   git clone git@github.com:myzenon/zestack.git .zestack/core
   ```

   If SSH fails, for example on a machine without a GitHub SSH key, tell the human and use HTTPS instead. The repo is public, so HTTPS needs no login:

   ```
   git clone https://github.com/myzenon/zestack.git .zestack/core
   ```

   Then, in both modes, write the zestack commit hash (`git -C .zestack/core rev-parse HEAD`) to `.zestack/core/VERSION` and delete `.zestack/core/.git/`. In git mode, a repo inside the project's repo would be committed as a bare pointer, so teammates would get an empty `core/`. In self-sync mode, Obsidian Sync doesn't sync hidden folders, so `.git/` wouldn't reach other machines anyway. The hash keeps the installed version known.
5. **Load zestack's `CLAUDE.md`.** Check what the root already has (a `CLAUDE.md`, a `CLAUDE.local.md`, whether each is committed), then suggest one way and ask the human to choose. A wrong choice either changes the team's files or leaves zestack unloaded. The ways:
   - Add the line `@.zestack/core/CLAUDE.md` to the root `CLAUDE.md`, creating it if missing. Fits git mode, because the team gets it too.
   - Put that line in `CLAUDE.local.md` and add `CLAUDE.local.md` to `.git/info/exclude`. Fits self-sync mode, because the team's files stay untouched. Not yet confirmed whether `CLAUDE.local.md` loads when there is no `CLAUDE.md`.
   - Create a root `CLAUDE.md` with only that line and add it to `.git/info/exclude`. Self-sync mode, only when the repo doesn't commit a `CLAUDE.md`.

6. **Link the skills.** For each skill folder in `.zestack/core/skills/`, link `<root>/.claude/skills/<skill> -> ../../.zestack/core/skills/<skill>`. Claude Code finds project skills in `.claude/skills/` and follows symlinked skill folders, and a link to the folder means content changes need no re-linking. In git mode, commit the links, so the team gets them. In self-sync mode, add each link to `.git/info/exclude`. With a workspace root that holds several repos, tell the human to start Claude Code at the workspace folder, because skill search stops at a repo's root.
7. **Turn off auto memory.** Add `"autoMemoryEnabled": false` to the root's `.claude/settings.local.json`, creating it if missing. This file is per machine, so if `git check-ignore` shows it isn't ignored, add it to `.git/info/exclude`. Claude Code's auto memory is on by default and saves to the local machine, which breaks zestack's stateless principle. Knowledge goes through the `knowledge-manager` skill instead.
8. **State.** Create `.zestack/state/`. In git mode, add `.zestack/state/work/*/tmp/` to the root `.gitignore`, so each Work's scratch files never reach the repo.
9. **Existing project.** If the project already has code, such as another team's project, its phase 1 was done by other people. Read the current system and fill in the state files (`requirements.md`, and `technical.md` and `code-design.md` per project), recording what and why as far as the code shows. If the project has files from another harness or planning setup (for example an agenda or backlog), move what fits into the matching state: current work into a Work, decisions into the phase 1 files or knowledge, and anything else into `.zestack/state/notes/`, one file per note. The human reviews them as a diff. Then ask the human which phase fits and write `phase.json`. For a new project, skip this: `CLAUDE.md` asks for the phase at the first session.
10. **Check.** Ask the human to start a new session and run `/memory` (loaded memory files, and whether auto memory is on) and `/skills` (loaded skills), to confirm zestack's `CLAUDE.md` and its skills are there and auto memory is off. If auto memory is still on, the project setting didn't take effect: ask the human to turn it off with the `/memory` toggle, which saves it in their user settings.
