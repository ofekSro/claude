# Claude Code agents and skills for engineering calculation tools

Custom subagents and skills for Claude Code, written for Python structural-engineering tools
(blast, impact, SDOF) with tkinter or PySide/PyQt GUIs.

## Install

Copy `agents/` and `skills/` into your user-level Claude folder so they are available in every project.

Windows (PowerShell):

```powershell
.\install.ps1
```

Linux / macOS / Git Bash:

```bash
./install.sh
```

Both scripts copy the files to `~/.claude/agents/` and `~/.claude/skills/`, overwriting older copies of the same names and touching nothing else.

## Agents

| Agent | Edits code | Purpose |
| --- | --- | --- |
| `eng-code-simplifier` | yes | Simplifies calculation code without changing any numerical result; adds short English comments citing equations and standards. Supports "review only". |
| `arch-reviewer` | no | Maps modules and dependencies, writes `docs/ARCHITECTURE_REVIEW.md` with a phased migration plan to a layered architecture. |
| `arch-refactorer` | yes | Executes one phase of that plan, with characterisation tests and a commit. |
| `gui-ux-reviewer` | no | Reconstructs user flows from the GUI code and writes `docs/UX_REVIEW.md` with prioritised findings, tkinter and Qt specific. |
| `gui-qa-tester` | no | Launches the real GUI, screenshots it, drives the flows, compares displayed numbers with the core functions. Report under `docs/qa/`. |
| `task-planner` | no | Reads `TODO.md` / `DONE.md`, picks the next batch of related tasks, writes acceptance criteria. |
| `task-implementer` | yes | Implements a whole batch without stopping, one commit per task. |
| `task-verifier` | yes | Independently re-checks every criterion, reviews the diff, fixes what fails. |
| `section-planner` | no | Thesis writing: turns an agreed roadmap for one LaTeX subsection into `plans/<label>.md`, one claim, evidence and transition per paragraph. |
| `paragraph-writer` | yes | Thesis writing: writes or rewrites one paragraph from the plan under a `% [Pn]` anchor, in the project's CLAUDE.md style, citing only existing bib keys. |
| `flow-reviewer` | no | Thesis writing: fresh-eyes review of a subsection's argument (review mode) or of its fit with the chapter and thesis (fit mode). Numbered, line-anchored findings. |
| `research-auditor` | no | Scientific audit of a research repo through one lens: `algorithm` (code vs docs vs thesis), `physics` (units, scaling, reference data) or `choices` (thresholds, criteria, estimators and their justification). Writes `docs/audit/<date>/<lens>.md`. |
| `stats-auditor` | no | Audit of the regression and model-selection methodology: leakage, selection on the test set, unit of observation, metrics, uncertainty, extrapolation. |
| `repro-checker` | no | Runs fast tests and a short pipeline into scratch, checks anchor tests really ran, diffs regenerated tables against committed results of record. |
| `traceability-mapper` | no | Builds `docs/TRACEABILITY.md`: every thesis claim mapped to code, test and output file with a status. Reads the thesis only at paths the owner names. |

## Skills

| Skill | What it does |
| --- | --- |
| `/refactor` | Runs arch-reviewer, gui-ux-reviewer and gui-qa-tester, then executes the plan one approved phase at a time with simplification, tests and QA after each. |
| `/gui-qa` | Real render-and-drive QA of the GUI, shows screenshots and failures. |
| `/todo` | Works through `TODO.md` in batches: plan, implement, verify, simplify, QA, then moves finished tasks to `DONE.md` with details. |
| `/ref` | Registers reference documents (manuals, standards) under `docs/references/` with an index that every agent reads first. |
| `/section` | Thesis writing, one LaTeX subsection at a time: `plan`, `write`, `review`, `fit`, `apply`, `status`. The roadmap is agreed in chat, the plan is a file, the review is a separate agent. |
| `/verify` | Scientific audit of a research repo: five read-only lenses in parallel, a summary, `trace` for the thesis matrix, and `fix <id>` with an explain-then-approve flow for each finding. |
| `/worklog` | Appends a dated Hebrew entry to `WORKLOG.md` from the current conversation, only when the owner asks. `draft` previews, `show` reads. |
| `/tidy` | Proposal-first code tidying: review-only simplification proposals per file, `structure` for the repo layout, `apply <file> <items>` with before/after numerical comparison. |

## Models

Each agent pins its model in its frontmatter. `opus` for anything that needs engineering, scientific or editorial judgement: the auditors, planners, verifiers, refactorer, thesis planner, writer and reviewer. `sonnet` for mechanical work that is verified by numbers or tests anyway: simplifier, GUI QA and UX review, reproducibility check, traceability mapping. To use a different model for one agent, edit its `model:` line (`sonnet`, `opus`, `haiku`, or a full model id such as `claude-fable-5-1`).

## Conventions the agents rely on

- Git is required for `/refactor` and `/todo`; every step is a commit.
- Numerical results, coefficients, units and validity ranges are never changed without a cited source. Disagreements go to `docs/ENGINEERING_QUESTIONS.md`.
- `docs/references/INDEX.md` lists the reference documents. A `ref: <id>` tag on a `TODO.md` line binds a document to a task.
- Code comments and docstrings are in English and cite the standard or manual section.
