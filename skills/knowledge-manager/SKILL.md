---
name: knowledge-manager
description: Reads, saves, updates, or cleans project knowledge in .zestack/state/projects/<project>/topics/ (rules, system facts, decisions). Use when the human asks to look up, use, save, or remember knowledge, or when a workflow requires a knowledge check. Not for ordinary work discussion or broad repository exploration.
---

# Knowledge manager

Knowledge is kept as plain files in `.zestack/state/`, so it travels with git or sync and any AI can read it. Never save knowledge to an AI's own memory, such as Claude Code's auto memory, because that stays on one machine and one agent.

## Shape

```text
.zestack/state/projects/<project>/topics/
├── index.md          short routing: one line per topic
└── <topic>/
    ├── rule.md       constraints: what must or must not be done
    ├── doc.md        system facts: features, flows, call chains
    └── why.md        decisions and rejected alternatives
```

Phase 1's decisions live in `technical.md` and `code-design.md`. Topics hold everything else the human wants kept.

## Focused read (default)

Pick one project and one question. Read that project's `topics/index.md`, then only the topic files that match the question. Don't scan other projects or all topics.

Read `rule.md` only for constraints, `doc.md` only for facts, and `why.md` only for a decision or a rejected alternative. Return a short packet: the files used, the rules and facts that apply, anything uncertain or stale, and any conflict. Reuse the packet while the project and question stay the same.

If the project isn't clear and it changes the answer, ask the human one short question.

## Rare operations

- Saving or updating knowledge: read `references/write.md`.
- Cleanup, deduplication, or reorganizing: read `references/cleanup.md`.

Don't write source code, Works, Tasks, or `CLAUDE.md` from this skill.
