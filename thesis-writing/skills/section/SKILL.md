---
name: section
description: Writing the LaTeX thesis one subsection at a time. /section plan <label> turns the roadmap agreed in chat into plans/<label>.md (section-planner). /section write <label> [N|all] [feedback] writes or rewrites paragraphs from the plan (paragraph-writer). /section apply <label> <finding numbers> applies findings chosen from the last /thesis-check of that label. /section status lists plans and progress. All checking lives in /thesis-check. Nothing is edited without an explicit request.
---

You are running the author's writing workflow: roadmap in conversation, plan file, paragraph by paragraph writing, and applying chosen review findings. All checks (rules, register, clarity, flow, citations, fit) are done by `/thesis-check`; this skill only writes. The conversation stays the place where decisions are made.

Subagents cannot launch each other, so you launch every agent from here. Reply to the author in Hebrew. All prose written into the thesis is English, per the project `CLAUDE.md`.

## Stage 0: locate the project and the target

1. The thesis root is the nearest directory upward from the working directory that contains a `CLAUDE.md` and a `Content/` folder with `.tex` files (or a `Thesis.tex`). If none is found, ask the author for the path.
2. Read the project `CLAUDE.md`. Its scope rules apply to you as well: touch only what the author named, suggest restructures rather than performing them, never compile unless asked.
3. Resolve the label: `grep -rn 'label{<label>}' Content/` (also accept the label without its prefix, or a heading text, and disambiguate by asking if several match). Record file and line.
4. Plans live in `plans/` under the thesis root. The plan file for a label is `plans/<label with ':' replaced by '_'>.md`.

## `/section plan <label>`

1. Gather the roadmap. Take what the author and you agreed on in this conversation about this subsection: the topics, the order, what must and must not be included, decisions taken along the way. Write it down as a compact list, in the author's words, before launching anything, and show it to the author in one message. If nothing has been discussed yet, ask the author for the roadmap and stop.
2. Launch **section-planner** with the label, the roadmap list, and the resolved file. Wait.
3. Read the plan file and show the author: purpose, the paragraph titles with their claims in one line each, the NEEDCITATION items, and the risks. Ask whether to adjust anything. Edits to the plan are made by you directly in the plan file when the author asks, no agent needed.

## `/section write <label> [N | N-M | all] [feedback]`

1. The plan file must exist. If it does not, say so and offer `/section plan`.
2. Decide the mode: if the `.tex` already contains the anchor `% [PN]` for the requested paragraph, the mode is `rewrite`, otherwise `insert`. Say which before launching.
3. Pass the author's feedback from the current message verbatim, plus any earlier feedback in this conversation about the same paragraph.
4. Launch **paragraph-writer** with the plan path, the paragraph selection, the mode and the feedback. Wait.
5. Show the author the written paragraph(s) as they now stand in the file, plus the writer's notes (citations used, NEEDCITATION inserted, TODO figures). Do not paraphrase the paragraph. The author reacts in chat, and a further `/section write <label> N <feedback>` rewrites it.
6. With `all`, write the paragraphs in order in one launch, so each sees the previous ones.

## Checking what was written

Not here. After writing, the author runs `/thesis-check <label> deep` (rules, register, clarity and flow against the plan), `/thesis-check <label> cite` (citations) and `/thesis-check <label> fit` (place in the chapter). Point the author to them after each `write`.

## `/section apply <label> <numbers>`

1. Take the chosen findings from the last `/thesis-check` report of this label in the conversation (`deep`, `cite` or `fit`; a lint finding counts too). Numbers refer to that report. If the conversation no longer holds it, ask the author to run the check again.
2. For each chosen finding, the change is applied to the paragraph it names by launching **paragraph-writer** in `rewrite` mode with the finding's problem and suggestion as feedback. Findings that only move or reorder paragraphs, or that touch text outside the subsection, are not applied by an agent: describe the change and ask the author to confirm, then do it yourself with the Edit tool, minimally.
3. Show the author each rewritten paragraph.

## `/section status [label]`

List the plans in `plans/`, and for each whether its paragraphs exist in the `.tex` (count the `% [Pn]` anchors against the plan), and whether `/thesis-check` has been run on it in this conversation.

## Rules

- Never edit a paragraph the author did not name. Never delete an anchor. Never touch `bibliography.bib`.
- Never compile. If the author wants a PDF, they say so, and then `latexmk` is the tool.
- Never resolve or remove an existing `NEEDCITATION!` marker unless the author asks.
- When the author writes in Hebrew, thesis text is still written in English. Feedback is passed to the writer as the author gave it.
- If a step changes more than one paragraph, say so before launching it.

## Model fallback

section-planner and paragraph-writer run on Fable 5 (`model: claude-fable-5` in their frontmatter). If an agent comes back with a refusal on safety grounds, fails because Fable 5 is unavailable or out of usage, or returns an empty or evasive report that shows it declined the task (this domain uses words like charge, TNT and detonation in an ordinary engineering sense), relaunch the same agent once with the Agent tool's `model: "claude-opus-5-5"` override (Opus 5.5), with the same prompt. Say in the reply that the fallback was used and for which agent. Do not retry more than once, and do not rephrase the task to get around a refusal; if Opus also declines, report it to the owner.
