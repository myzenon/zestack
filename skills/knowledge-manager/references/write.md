# Knowledge writes

Use this only after the human asks to save, update, or remember knowledge.

Write only in the selected project's `.zestack/state/projects/<project>/topics/`:

- `rule.md` for constraints
- `doc.md` for system facts, features, or call chains
- `why.md` for accepted decisions and rejected alternatives
- `index.md` for one short routing line per topic

Keep rule, fact, and reason in their own files, because a reader looking for one shouldn't have to read the others. Keep existing content unless the request clearly replaces it. When a new decision replaces an old one, delete the old text in the same write.

Every fact carries its source mark, as `CLAUDE.md` describes: `(tested by the human)`, `(from docs: <link>)`, `(from code: <path>)`, or `(AI guess, not checked)`.

Every topic file starts with `<!-- last-verified: COMMIT_HASH -->`, so a reader can tell how old it is. When the human gives no hash, use the project repo's current `HEAD`.
