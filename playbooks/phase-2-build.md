# Phase 2: Build features

Goal: build the remaining features quickly on the base settled in phase 1. Because the technology and structure are proven, the human trusts the AI more here, so the AI can produce more code per step, and the human reviews faster.

## How to work

- Each feature is a Work. Inside it, do a lighter version of phase 1's thinking: what the feature needs, and how it fits the existing design.
- Write code that follows `code-design.md`, so the human's review is mainly checking that the code fits the known pattern.
- Subagents are allowed in this phase.
- Usual changes are small tweaks within the existing system, such as adjusting a formatter rule. Engine-level changes, such as replacing the formatter, are rare. They're allowed, but point them out clearly to the human, because they touch what phase 1 settled. When one is agreed, update `technical.md` or `code-design.md` with what changed and why, so the state doesn't go stale.

The human decides when to move to phase 3. When they do, update `phase.json`.
