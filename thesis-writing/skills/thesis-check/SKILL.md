---
name: thesis-check
description: Quality check of the LaTeX thesis against the rules in its CLAUDE.md. /thesis-check [chapter] runs the lint script for the mechanical rules and thesis-style-reviewer for the judgement rules (clarity, paragraphs, attribution, captions, hyphenation, symbols), per chapter in parallel. /thesis-check lint runs only the script. /thesis-check needcite finds sources in Papers/ for NEEDCITATION markers and missing cite keys. /thesis-check build compiles, reads the log and looks at the pages. Read-only; never edits the thesis.
---

You check the owner's thesis against the rules in the thesis `CLAUDE.md`. Reply in Hebrew. Never edit `.tex` or `.bib` files. Compile only for `/thesis-check build`, which is the owner's explicit request.

## Stage 0: locate

1. The thesis root is the nearest directory upward with a `CLAUDE.md` and a `Content/` folder (or a main `.tex`). If none, ask for the path.
2. The lint script `lint.py` sits next to this SKILL.md. Look for it at `.claude/skills/thesis-check/lint.py` under the thesis root first, then at `~/.claude/skills/thesis-check/lint.py`.
3. The chapters are those the main `.tex` loads with `\input` (the script finds them). Drafts such as `temp*.tex` or `*_new.tex` are never checked.

## Choosing the target

- No argument or `all`: every chapter.
- A chapter: its number (`9`), its file name (`9.ParametricStudy.tex`) or a label inside it (`sec:...`, `ssec:...`); a label narrows the style review to that section.

## `/thesis-check [target]`

1. Run the script: `python <lint.py> <thesis root> [chapter files] --json`. Keep the JSON.
2. Launch **thesis-style-reviewer** once per chapter in the target, in parallel (up to about six at a time), skipping front matter (title, acknowledgements, acronym list, symbol list). Give each its chapter path, the lint findings for that chapter (so it does not repeat them), and the list of earlier chapters.
3. Report in Hebrew, per chapter, in this order:
   - **שגיאות** (lint severity `error`): duplicate labels, undefined references, cite keys not in the bibliography, floats without caption or label. These break the document.
   - **הפרות כללים** (lint severity `rule`), grouped by rule with counts and locations. Long lists (for example forty spelling hits) are shown as a count with the first ten.
   - **ממצאי בהירות** from the reviewer, in full, numbered.
   - **לבדיקה** (lint severity `check`): long sentences and paragraph lengths, which the owner judges.
   - **NEEDCITATION**: count and locations, with a pointer to `/thesis-check needcite`.
4. End with a one-line total per chapter. Do not fix anything. If the owner wants a paragraph rewritten, that is `/section write <label> N "<feedback>"`.

## `/thesis-check lint [target]`

Only the script, printed in its readable form (without `--json`), summarised in Hebrew. Seconds, no agents.

## `/thesis-check needcite [target]`

1. Run the script with `--json` and collect the `needcitation` and `cite-key-not-in-bib` findings in the target.
2. For each, take the whole sentence around the marker (from the previous full stop to the next one).
3. Launch **citation-finder** with the list, the `Papers/` folder, the bibliography path, and `docs/references/` if it exists. Split into a few parallel batches when there are more than about ten markers.
4. Report the candidates as returned. Remind the owner that a source with no bib entry must be added to `bibliography.bib` by them before it is cited. Do not insert any citation.

## `/thesis-check build`

1. Launch **latex-builder** for the thesis root.
2. Report its findings. For every undefined reference or duplicate label, also give the lint location, since the script points at the source line.

## Rules

- Read-only. No edits to the thesis, its bibliography, or its CLAUDE.md.
- No compilation outside `build`.
- Hebrew in replies, English for any proposed thesis text, which follows the thesis style rules (British English, no semicolons, third person).

## Model fallback

thesis-style-reviewer and citation-finder run on Fable 5 (`model: claude-fable-5`). If one comes back with a refusal on safety grounds, fails because Fable 5 is unavailable or out of usage, or returns an empty report, relaunch it once with the Agent tool's `model: "claude-opus-5-5"` override and the same prompt, and say in the reply that the fallback was used. Do not rephrase the task to get around a refusal; if Opus 5.5 also declines, report it to the owner.
