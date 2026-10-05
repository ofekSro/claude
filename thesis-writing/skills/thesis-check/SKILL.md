---
name: thesis-check
description: Every check of the LaTeX thesis, read-only. /thesis-check [target] runs only the lint script (mechanical rules and register profile, no model cost). /thesis-check <target> deep adds one reviewer for register, clarity and the flow of the argument (against the section plan when one exists). /thesis-check <target> cite checks that cited sources support the sentences, with page and quote. /thesis-check <label> fit checks a section against its chapter and the thesis. /thesis-check needcite finds sources in Papers/ for NEEDCITATION markers. /thesis-check build compiles and inspects problem pages. A target is a chapter number, a chapter file, a section label, or for cite also a line range or a bib key.
---

You check the owner's thesis. Reply in Hebrew. Never edit `.tex` or `.bib` files: fixes are made with `/section write` or `/section apply`. Compile only for `/thesis-check build`, which is the owner's explicit request.

The skill is economical by design: the script does everything a script can, agents run only when a mode asks for them, and agents receive short prepared inputs instead of searching on their own.

## Stage 0: locate

1. The thesis root is the nearest directory upward with a `CLAUDE.md` and a `Content/` folder. If none, ask for the path.
2. The scripts `lint.py` and `extract_papers.py` sit next to this SKILL.md. Look first at `.claude/skills/thesis-check/` under the thesis root, then at `~/.claude/skills/thesis-check/`.
3. The chapters are those the main `.tex` loads with `\input`. Drafts are never checked.
4. The register card is `.claude/register_card.md`. It is fixed by the owner and never regenerated. Only a thesis without it falls back to a generated card in `.claude/cache/register_card.md` (`lint.py --card`).
5. Cache folder `<thesis root>/.claude/cache/`: `papers/`, derived files that the scripts keep current and nobody edits by hand.
6. Plans from `/section plan` live in `plans/<label with ':' as '_'>.md`.

## Targets

- none or `all`: every chapter.
- a chapter number (`9`) or file name (`9.ParametricStudy.tex`).
- a section label (`ssec:PrS_Method`): lint findings are filtered to the section's line range, and agents work on that section only. The normal way to check what was just written.
- for `cite` only, also `<file>:<line>`, `<file>:<from>-<to>`, or `key <bibkey>` (every sentence that cites that key).

Every report numbers its findings, so the owner can apply them with `/section apply <label> <numbers>`.

## `/thesis-check [target]` (default: lint only)

1. Run `python <lint.py> <root> [chapter file] --json`.
2. Report in Hebrew:
   - **Register table**: the reference profile (frozen in the fixed card when there is one), then one row per chapter in the target with its profile and flagged drift. One line explaining the columns. "Too short to compare" rows without judgement.
   - **שגיאות** (severity `error`).
   - **הפרות כללים** (severity `rule`), grouped by rule. A rule with more than ten hits shows the count and the first ten.
   - **לבדיקה** (severity `check`): long sentences, paragraph lengths, intensifiers. Count and the first five of each.
   - **NEEDCITATION**: count, with a pointer to `needcite`.
3. End with the next useful command for this target (`deep`, `cite` or `fit`).

## `/thesis-check <target> deep`

1. Run the lint as above.
2. Register card: use `.claude/register_card.md`. Never modify it. Only if it does not exist, use `.claude/cache/register_card.md`, generating it with `python <lint.py> <root> --card` when missing.
3. Launch **thesis-style-reviewer** once per chapter in the target, or once for a section label, in parallel when there are several, front matter excluded. Give each, and nothing more:
   - the chapter path, and the section label if the target is a section;
   - the plan path if `plans/<label>.md` exists for that section;
   - the path of the register card;
   - this chapter's lint findings, compactly (rule, line, matched words), so it does not repeat them;
   - this chapter's register profile row and the reference profile;
   - the `definitions` entries from the lint JSON that matter to this chapter: those first appearing in this chapter or later, plus every symbol and acronym it uses.
4. Report the lint part as in the default, then **משלב, בהירות וזרימה** from the reviewer in full.
5. For a whole-thesis deep run, say before launching how many reviewers will run.

## `/thesis-check <target> cite`

Whether each cited source supports the sentence that cites it, and where in the source the claim is.

1. **Collect.** Find every citation command in the target (`\cite`, `\citep`, `\citet`, `\textcite`, `\parencite`, `\autocite`, `\citeauthor`, `\citeyear`, several keys per command), ignoring comments. For each, take the whole sentence that carries it, with file and line. Group by key and give a one-line count.
2. **Match keys to PDFs.** From each bib entry take the first author's surname, the year and the title, and find the PDF in `Papers/` by surname and year, then by title words. If a match is uncertain, show the key-to-file table and let the owner correct it before continuing.
3. **Refresh the text cache**: run `python <extract_papers.py> <root>`. Only new or changed PDFs are extracted.
4. **Verify.** Launch one **citation-verifier** per key, in parallel (up to about six at a time), each with the key, the bib entry, the PDF path or "none", the cached text path `.claude/cache/papers/<pdf stem>.txt`, and its citing sentences.
5. **Report**: a table of file:line, key, verdict, page. Then in full every claim not marked **נתמך**: the sentence, the quote, the gap and the suggested rewording. Then the keys with no PDF. Then, compactly, page and quote for the supported claims.

Verdicts: **נתמך**, **נתמך חלקית**, **לא נמצא**, **המקור טוען אחרת**, **מקור משני**. Sources without a PDF are marked "אין קובץ" and never judged from memory.

## `/thesis-check <label> fit`

How the section sits in the chapter and the thesis.

1. Launch **flow-reviewer** in `fit` mode with the label and the plan path if it exists.
2. Report its findings as returned: roadmap promise, entry from the previous section, exit to the next, references in and out, consistency of numbers and definitions with the rest of the thesis, redundancy with other chapters.

## `/thesis-check lint [target]`

The script's readable output (without `--json`), summarised in Hebrew. Seconds, no agents.

## `/thesis-check needcite [target]`

1. Run `python <extract_papers.py> <root>`.
2. Run the lint with `--json` and collect `needcitation` and `cite-key-not-in-bib` in the target, each with its full sentence.
3. Launch **citation-finder** with the list, the cache folder `.claude/cache/papers/` and the bibliography path. Split into parallel batches only above about ten markers.
4. Report the candidates as returned. A source with no bib entry must be added to `bibliography.bib` by the owner before it is cited. Do not insert any citation.

## `/thesis-check build`

Launch **latex-builder** for the thesis root. Report its findings, and for each undefined reference or duplicate label give the lint location too.

## Rules

- Read-only on the thesis and its bibliography. The only files written are the derived cache files above.
- No compilation outside `build`.
- Hebrew in replies, English for any proposed thesis text, in the thesis style.
- Long books read slowly in `cite`; if a cited key is a book, suggest registering it once with `/ref add`.

## Model fallback

thesis-style-reviewer runs on Opus 5.5 (`model: claude-opus-5-5`); if Opus 5.5 is unavailable or out of usage, relaunch it once with the Agent tool's `model: "claude-fable-5"` override. citation-verifier, citation-finder and flow-reviewer run on Fable 5; if one refuses on safety grounds, fails because Fable 5 is unavailable or out of usage, or returns an empty report, relaunch it once with `model: "claude-opus-5-5"`. latex-builder runs on Sonnet and needs no fallback. Say in the reply when a fallback was used. Do not rephrase a task to get around a refusal; if the fallback also declines, report it to the owner.
