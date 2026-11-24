# Phase 1: Design and proof

Goal: the human and AI see the same big picture and prove the design works, before building features at speed. Review in this phase is intensive, because every later feature builds on these decisions.

Each step ends by writing its decisions to a file in `.zestack/state/`. Record what was decided and why, for example "Postgres, because billing needs relational joins." Session context is lost when a session ends, and a later session or another agent that sees only the what might change a decision without knowing what it would break. Before starting a step, read its file if it exists, so you build on decisions already made.

## Steps

1. **Requirements (the what).** Agree on the final goal, the project scope, and each feature roughly. Write to `.zestack/state/requirements.md`, one file for the whole root.
2. **Technical (the how).** Decide the technology this project's requirements actually need. The examples below are a starting point, not a checklist: skip what doesn't apply to this project, and raise anything important that's missing. Write to `.zestack/state/projects/<project>/technical.md`, one file per project. Also write `.zestack/state/projects/<project>/project.md` with `Path:` (the project's code folder, relative to the root) and `What it is:` (one line), so the AI can tell which project a changed file belongs to.
   - Language and runtime: TypeScript on Node, Python, Go
   - App: frontend framework (Next.js, Vue, React), backend framework, API style (REST, GraphQL, RPC)
   - Data: database engine (Postgres, SQLite, DynamoDB), ORM or query layer, migrations, caching
   - Platform: cloud stack (AWS EC2 or ECS, Vercel, Cloudflare), deployment, environments, secrets
   - Quality: linter, formatter, type checking, test engine, whether to have E2E tests, CI/CD
   - Cross-cutting: authentication, logging and monitoring, error tracking, package manager, monorepo or not
   - Other project types: a CLI needs a distribution method (npm, Homebrew), a library needs publishing and versioning, a mobile app needs app store delivery
3. **Code design.** Agree on how the code itself is shaped. The human loves to code, so these choices matter to them as much as the technology. The examples below are a starting point, not a checklist: skip what doesn't apply to this project, and raise anything important that's missing. Write to `.zestack/state/projects/<project>/code-design.md`, one file per project.
   - Folder structure: by feature or by layer, where tests live, shared code
   - System structure: layered, hexagonal (ports and adapters), MVC, repository pattern, service layer
   - Paradigm: OOP, functional, or a mix, and where each is used
   - Module boundaries: what each module owns, how modules depend on each other, dependency injection
   - Data and types: how domain models are defined, where external data is validated
   - Error handling: exceptions or result types, where errors are caught
   - State: where state lives, how it changes (for example, in a frontend store or on the server), and how it's modeled (for example, one status field with allowed moves, or separate flags)
   - Naming: files, functions, types
4. **Proof.** Build one or two real features on top of the design, each as a Work.
   - If they work and fit well, the design is settled.
   - If they cause trouble, change the idea, concept, or system, update the affected state file, and go back to the step that needs it.

Phase 1 is a loop: design, prove, adjust. It's only finished when the proof works. The human decides when to move to phase 2. When they do, update `phase.json`.
