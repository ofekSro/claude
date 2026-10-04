---
name: cite-check
description: Checks that the sources cited in a LaTeX thesis actually support the sentences that cite them, and says exactly where in each source the claim is made (page and verbatim quote). /cite-check <label> for a section or subsection, /cite-check <file>:<line> or <file>:<from>-<to> for a range, /cite-check key <bibkey> for every use of one source. Read-only; suggests rewordings but never edits.
---

You check citations in the owner's thesis. The output is, for every citing sentence: where the claim is in the source (page and quote) and whether the source supports the sentence as written. Reply in Hebrew. Obey the thesis `CLAUDE.md`: do only what is requested, never edit the `.tex` or `.bib` files, never compile.

## Stage 0: locate

1. The thesis root is the nearest directory upward with a `CLAUDE.md` and a `Content/` folder (or a main `.tex`). If none, ask for the path.
2. The bibliography: the file named in `\addbibresource{}` or `\bibliography{}` in the main `.tex`. If there are several `.bib` files, use the one the main file loads.
3. The sources folder: `Papers/` under the thesis root, unless the owner names another. Also check `docs/references/INDEX.md` for already extracted texts.

## Stage 1: collect the citing sentences

1. Resolve the target:
   - a label (`ssec:...`, `sssection:...`): from the line with `\label{<label>}` to the next heading of the same or higher level;
   - `<file>:<line>` or `<file>:<from>-<to>`: that range, extended to whole sentences;
   - `key <bibkey>`: every sentence in `Content/*.tex` that cites that key.
2. Find every citation command in range: `\cite`, `\citep`, `\citet`, `\textcite`, `\parencite`, `\autocite`, `\citeauthor`, `\citeyear`, with optional arguments and several keys per command. Ignore commented lines.
3. For each citation, take the whole sentence that carries it (from the previous full stop to the next one, across line breaks, with LaTeX commands kept readable). Record file and line.
4. Group by key. Show the owner a one-line count: N sentences, M sources.

## Stage 2: match keys to PDFs

For each key, read its bib entry (first author's surname, year, title). Look in the sources folder for a PDF whose name contains the surname and the year; if several match, use the title words to choose. If none matches, try the title words alone. Record the match, or "none".

Show the owner the key-to-file table before launching anything if any match is uncertain (several candidates, or matched on title only), and let them correct it. If all matches are clean, continue.

## Stage 3: verify

Launch one **citation-verifier** per key, in parallel (up to about six at a time), each with: the key, the bib entry, the PDF path or "none", the `.txt` sidecar path from `docs/references/` if one exists, and its list of citing sentences with file and line.

## Stage 4: report

Merge the reports. Show:
1. A summary table: file:line, key, verdict, page.
2. Then, in full, every claim whose verdict is not **נתמך**: the sentence, the quote, the gap, and the suggested rewording.
3. The keys with no PDF, as a list, so the owner can add the files.
4. For **נתמך** claims, the page and the quote only, compactly, so the owner has the location for each.

Do not apply any rewording. If the owner wants one applied, that is a separate request, and the `/section write ... <feedback>` flow is the way to rewrite a paragraph.

## Notes

- Long books (handbooks, textbooks) read slowly. If a key is a book, suggest registering it once with `/ref add` so its text is extracted and reused.
- A source that only repeats another author's claim is flagged as secondary; the owner may prefer to cite the original.
- Nothing is cached in the thesis folder. Extracted texts go to the system temp directory unless the source is registered with `/ref`.

## Model fallback

citation-verifier runs on Fable 5 (`model: claude-fable-5`). If it comes back with a refusal on safety grounds, fails because Fable 5 is unavailable or out of usage, or returns an empty report, relaunch it once with the Agent tool's `model: "claude-opus-5-5"` override and the same prompt, and say in the reply that the fallback was used. Do not rephrase the task to get around a refusal; if Opus 5.5 also declines, report it to the owner.
