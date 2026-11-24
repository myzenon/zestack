# State design (draft)

Decisions made so far. To be tuned later.

## Why state is needed

The AI has to know which phase a root is in, phase 1's decisions (requirements, technical, code design) and the progress of each Work have to survive the end of a session, a switch of machine, and a switch of agent. Session context loses all of these.

## Layout in a root

```
.zestack/
├── core/    zestack's files (CLAUDE.md, playbooks). Replaced by an update.
└── state/   this root's state. Never touched by an update.
```

## Root and projects

There is one `.zestack/` per root, and a root covers one or more projects:

| Setup | Where `.zestack/` lives | Projects |
|---|---|---|
| Single repo | the repo root | 1 |
| Monorepo | the repo root | N (packages) |
| Several repos | a workspace folder that holds the repos | N |

A Work has the same shape whether it touches one project or several (taken from no_vibe_agent's work-planner):

```
work/<id>/
├── work.md            the whole Work: outcome, approach
└── <project>/work.md  each project's part
```

## Files in state/

One file per item, so each diff stays small and the AI reads only what it needs. JSON for structured values, markdown for decisions written as prose, following the prompting guide's advice to use structured formats for state data and plain text for notes.

One layout for every root, so playbooks never branch on "single project or several". A single project has exactly one folder under `projects/`.

```
.zestack/state/
├── phase.json                 whole root: current phase, e.g. {"phase": 1}
├── requirements.md            whole root: phase 1, step 1
├── work/<id>/work.md          the Work system: one folder per Work
├── notes/                     anything that fits nowhere else; free form
└── projects/<project>/
    ├── project.md             Path: (code folder, relative to the root) and What it is: (one line)
    ├── technical.md           this project's phase 1, step 2
    ├── code-design.md         this project's phase 1, step 3
    └── topics/                knowledge (knowledge-manager skill): index.md, <topic>/rule.md, doc.md, why.md
```

Each decision records what was decided and why. A later session or another agent that sees only the what might change it without knowing what it would break. For example: "Postgres, because billing needs relational joins."

## Works

The progress system is the Work system (Work → Task → Focus, recorded in `work.md`), brought from the human's current harness (no_vibe_agent). Works don't depend on the phase: a phase can contain many Works (for example, 20 in phase 1, 500 in phase 2, 50 in phase 3), and the phase only changes how the AI behaves inside each Work. Phase 1's proof features are normal Works too. Details are not designed yet.

## Notes

`notes/` holds what the human wants kept but that fits nowhere else: not a Work, not knowledge, not a phase 1 decision. For example, future features and their rough order. It has no fixed files and no rules, on purpose: the human will find the real patterns by using it, and a concept can be designed from those later. Notes are not a source of truth and never the main context. The AI reads a note only when the human points to it, so it never acts on a note the human forgot. Work still starts as a new Work.

## Two modes

1. **Git mode.** `.zestack/` is committed in the project repo, without `.git/info/exclude`. State travels with git, and the team can see it.
2. **Self-sync mode** (name to be decided). `.zestack/` is excluded from the project's git, and it syncs through a tool the human runs, currently Obsidian Sync. The real folder lives in the Obsidian vault, and the project links to it, for example `/projects/a/.zestack -> /obsidian/projecta`. On Windows the human works in WSL.

## Versioning

Each root keeps its own copy of zestack in `.zestack/core/`, at the version it was installed with. Changes to the zestack repo don't affect existing projects until the human updates them.

- `playbooks/installation.md`: how the AI installs zestack into a project. For an existing project (for example, another team's), phase 1 was already done by other people, so the AI reads the current system and fills in the state files (what and why, as far as the code shows). The human reviews them as a diff, then `phase.json` is set to the phase that fits. The phase 1 playbook stays about designing only.
- `playbooks/update.md`: how the AI updates a project's `.zestack/core/` from the current zestack, without touching `.zestack/state/`. The human reviews the update as a diff.

## Open

- The details of the Work system: being designed in `work-design.md`.

Later items are listed in `README.md`.
