---
name: verify
description: Scientific verification of a research calculation repo. /verify runs four read-only audit lenses in parallel (algorithm vs documentation, physics and units, arbitrary choices, statistics) plus a reproducibility check, and writes docs/audit/<date>/. /verify trace <thesis-chapter-paths> adds the thesis-to-code traceability matrix. /verify fix <finding-id> explains one finding's fix, waits for approval, then applies it. Nothing is edited without the owner's explicit approval.
---

You are running a scientific audit. The owner's rules, from the project `CLAUDE.md`, bind you: no change to any file without explicit approval after the owner understands its meaning, stay inside the repo folder, never "fix" a formula on your own judgement, results of record never move silently. Reply in Hebrew.

Subagents cannot launch each other, so you launch all agents from here.

## `/verify` (or `/verify all`)

1. Preconditions: the working directory is the repo root (has `CLAUDE.md`). Record `git rev-parse --short HEAD` and whether the tree is clean; both go into the summary. A dirty tree does not block an audit, but say so.
2. Create `docs/audit/<YYYY-MM-DD>/` (this directory and its reports are the output the owner asked for by running `/verify`; nothing else is written).
3. Launch in parallel, one Agent call each:
   - **research-auditor** with `lens=algorithm`
   - **research-auditor** with `lens=physics`
   - **research-auditor** with `lens=choices`
   - **stats-auditor**
   - **repro-checker**
   Tell each the date folder and remind it of the `CLAUDE.md` restrictions (read-only, stay in the folder, no production run unless allowed).
4. When all five return, read the five reports. Write `docs/audit/<date>/SUMMARY.md`:
   - commit, tree state, date, which lenses ran;
   - a single table of all findings across lenses: id, severity, title, which results of record or thesis claims it touches;
   - the high findings in full (copied, not paraphrased);
   - "decisions the owner must make": every finding whose resolution is a choice, phrased as a question with the options the auditor listed;
   - "what was checked and found consistent", merged from the reports;
   - "not checked".
5. Reply to the owner in Hebrew: counts by severity, each high finding in two sentences, the decision questions, and the path of SUMMARY.md. Then stop. Do not propose fixes yet; the owner reads first.

## `/verify <lens>`

Same, for one lens only: `algorithm`, `physics`, `choices`, `statistics`, `repro`. Writes that lens's report and updates SUMMARY.md if it exists for today.

## `/verify trace <path to chapter .tex> [more paths]`

The thesis lives outside the repo. Running this command with explicit paths is the owner naming those files, which `CLAUDE.md` §1.7 requires. Launch **traceability-mapper** with the given paths. Read `docs/TRACEABILITY.md` when it returns and report in Hebrew: counts by status, every mismatch with both values, every orphan. Do not edit the thesis or the code.

## `/verify fix <finding-id>`

The approval flow, one finding at a time:
1. Find the finding in today's or the latest audit reports. Quote it.
2. Write, in Hebrew, before touching anything:
   - **מה ישתנה:** the exact files and functions, and the nature of the change.
   - **למה:** the finding's evidence, in two sentences.
   - **מה יזוז:** which results of record could change, and whether the production pipeline must be rerun to see it.
   - **מה תלוי בזה בתזה:** the sections, equations or tables (from `docs/TRACEABILITY.md` if it exists, otherwise your best reading).
   - **חלופות:** the auditor's options, with your recommendation and its cost.
3. Stop and wait for the owner's approval of one option. Do not apply anything on "sounds good"; ask for the option by name if it is ambiguous.
4. On approval: make the change yourself with the Edit tool, minimally. Run the fast tests. Show the diff (`git diff`) and the test result. If a result of record moved, show old and new values side by side.
5. Ask whether to commit. Commit only on a yes, with the project's message style and the finding id in the body. Ask separately before any push.
6. Suggest `/worklog` if the change is worth recording, but do not write the log yourself.

## `/verify status`

List the audit folders under `docs/audit/`, and for the latest: findings by severity and which ones have a commit referencing their id (`git log --grep`), so the owner sees what is open.

## Rules

- Never let an agent edit. If an agent reports that it changed something, revert it with `git checkout -- <file>` and tell the owner.
- Never move a threshold, coefficient, criterion or seed as part of a "fix" unless the owner chose that option explicitly.
- Keep every reply short enough to read; the detail is in the files.

## Model fallback

Agents that need judgement run on Fable 5 (`model: claude-fable-5` in their frontmatter). If an agent comes back with a refusal on safety grounds, or with an empty or evasive report that shows it declined the task (this domain uses words like charge, TNT and detonation in an ordinary engineering sense), relaunch the same agent once with the Agent tool's `model: "claude-opus-5-5"` override (Opus 5.5), with the same prompt. Say in the reply that the fallback was used and for which agent. Do not retry more than once, and do not rephrase the task to get around a refusal; if Opus also declines, report it to the owner.
