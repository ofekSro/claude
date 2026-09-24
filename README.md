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

## Skills

| Skill | What it does |
| --- | --- |
| `/refactor` | Runs arch-reviewer, gui-ux-reviewer and gui-qa-tester, then executes the plan one approved phase at a time with simplification, tests and QA after each. |
| `/gui-qa` | Real render-and-drive QA of the GUI, shows screenshots and failures. |
| `/todo` | Works through `TODO.md` in batches: plan, implement, verify, simplify, QA, then moves finished tasks to `DONE.md` with details. |
| `/ref` | Registers reference documents (manuals, standards) under `docs/references/` with an index that every agent reads first. |
| `/section` | Thesis writing, one LaTeX subsection at a time: `plan`, `write`, `review`, `fit`, `apply`, `status`. The roadmap is agreed in chat, the plan is a file, the review is a separate agent. |

## Conventions the agents rely on

- Git is required for `/refactor` and `/todo`; every step is a commit.
- Numerical results, coefficients, units and validity ranges are never changed without a cited source. Disagreements go to `docs/ENGINEERING_QUESTIONS.md`.
- `docs/references/INDEX.md` lists the reference documents. A `ref: <id>` tag on a `TODO.md` line binds a document to a task.
- Code comments and docstrings are in English and cite the standard or manual section.
