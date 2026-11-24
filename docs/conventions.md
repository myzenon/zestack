# Conventions: sources

Where each convention in `conventions/` (imported into `CLAUDE.md` through `conventions/index.md`) comes from, so a rule can be traced back. pstack sources refer to github.com/cursor/plugins, `pstack/`, at commit `ca782ed` (2026-11-24).

| Convention | Source |
|---|---|
| Commits | The human's own: Conventional Commits v1.0.0, used in every project. |
| No stale code | The human's own ("a new decision replaces the old one", applied to code). Same idea in pstack: `skills/principle-migrate-callers-then-delete-legacy-apis` and `skills/correct` ("Delete old ways and dead code an agent would copy"). |
| No comments | pstack `skills/no-comments` and its agent `agents/comment-sicko.md`. The keep list is taken from Comment Sicko's exceptions. |
| Smallest change | pstack `skills/principle-laziness-protocol` (both of its rules: consolidate decisions, minimize the diff). |
| No speculative code | pstack `skills/principle-subtract-before-you-add`, only its "design for observed usage, no speculative guards" part. Not taken: "remove complexity first, leave it simpler than you found it", because it widens a change beyond what the human asked, against Smallest change and the pair-coder principle. |
| Easy to read | pstack `skills/principle-minimize-reader-load`. Added: the project's `code-design.md` wins when they clash, because a project may choose layers on purpose in phase 1. |
| Fix root causes | pstack `skills/principle-fix-root-causes`. Changed: pstack fixes every place with the same fault; zestack reports them and asks first, because fixing them all widens the change beyond what the human asked. Not taken: "propose an always-on signal" after a deep dig. |
| Test behavior | pstack `skills/principle-test-behavior-not-implementation`. |
| Data shape first | pstack `skills/poteto-mode/SKILL.md`, Non-negotiables: "Code → name the data shape first." Changed: the AI shows the shape to the human before writing logic. |
| Match the surrounding code | `cursor-team-kit/skills/deslop` in the same repo (github.com/cursor/plugins), its "patterns inconsistent with the file and surrounding codebase" item. Its other items are covered by No comments and No speculative code, or are per-project style (`any` casts, early returns). Moved from the phase 2 playbook to all phases. |
| Two sketches across modules | pstack `skills/architect` (triggered in `poteto-mode` for code across a function boundary). Changed: the human picks between the two sketches instead of the AI, and only for changes across module boundaries. Not taken: "redesign instead of patching if workarounds repeat", and running `arena` for large designs. |
| Plain English | pstack `skills/technical-writing`, its core sentence rules and Global English part. Not taken: the document-mode (Diátaxis) and Google-style details. |
| No AI tells | pstack `skills/unslop`, the rules not already in Plain English. Changed: the ⁉️ question marker is allowed. Not taken: rule 26's ban on "harness", which is what zestack calls itself. |
| Co-author | The human's own. |

## Considered, not taken as conventions

| pstack source | Why not, and where it went instead |
|---|---|
| `skills/principle-model-the-domain` | Choosing a domain model is a design decision, so as a convention the AI would make it alone while coding. Added instead as an example in phase 1, step 3 (State: how it's modeled), so the human decides it in design. |
| `skills/principle-boundary-discipline` | Design decisions already covered: "where external data is validated" is a phase 1, step 3 example (Data and types), "pure core, thin shell" is a System structure choice there, and "no re-checking inside" is covered by No speculative code. |
| `skills/principle-type-system-discipline` | Depends on the language (pstack links it to its TypeScript skill), so it's a per-project choice for phase 1, step 3 (Data and types). "Parse at the boundary" is the boundary-discipline part already skipped, and "derive from the schema, don't copy" is covered by Smallest change. |
| `skills/principle-make-operations-idempotent` | Skipped for now: the human was 50/50. Would apply only to state-changing operations (migrations, scripts, jobs). Can be revisited. |
| `skills/principle-prove-it-works` | Skipped for now: the human felt it fits phase 2 and later, a little toward vibe coding. Suggested form if revisited: when the AI says something works, it says what it ran and what it saw. A plain "always verify" rule would go against the Opus 5 guide's advice not to add re-check instructions. |
| `skills/tdd` | Skipped by the human. It's a bug-fix workflow: failing test first when a cheap test path exists, never bend tests to fit the code. |
| `skills/typescript-best-practices` | TypeScript only, so it belongs to a per-project extension (see "Extendable zestack" in `README.md`), not the harness. |
