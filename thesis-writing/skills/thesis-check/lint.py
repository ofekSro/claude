#!/usr/bin/env python3
"""Mechanical checks of the thesis CLAUDE.md rules. Read-only.

Usage:
    python lint.py <thesis_root> [chapter.tex ...] [--json]
    python lint.py <thesis_root> --card      write .claude/cache/register_card.md

With no chapter arguments, every chapter the main .tex loads is checked.
Drafts (temp*, *_old, *_new) are never checked. The JSON output also carries
the register profile and a definitions index (first appearance of every
symbol, acronym and emphasised term), so the style reviewer does not have
to search earlier chapters itself.
Only rules that a script can decide reliably live here. Judgement rules
(clarity, paragraph continuity, attribution, hyphenation by role) are
left to the thesis-style-reviewer agent.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------- spelling
IZE_OK = {"size", "sizes", "sized", "sizing", "prize", "prizes", "seize", "seized",
          "seizes", "seizing", "capsize", "capsized", "baize", "maize", "resize",
          "resized", "downsize", "oversize", "oversized", "undersized"}
WORD_FIXES = {
    # -or / -er / single l / other American forms -> British
    "behavior": "behaviour", "behaviors": "behaviours", "behavioral": "behavioural",
    "color": "colour", "colors": "colours", "colored": "coloured", "colorbar": "colour bar",
    "vapor": "vapour", "neighbor": "neighbour", "neighbors": "neighbours",
    "neighboring": "neighbouring", "neighborhood": "neighbourhood",
    "favorable": "favourable", "favor": "favour", "favors": "favours", "favored": "favoured",
    "labor": "labour", "honor": "honour", "humor": "humour", "rumor": "rumour",
    "armor": "armour", "flavor": "flavour",
    "center": "centre", "centers": "centres", "centered": "centred", "centerline": "centreline",
    "meter": "metre", "meters": "metres", "fiber": "fibre", "fibers": "fibres",
    "liter": "litre", "liters": "litres", "theater": "theatre",
    "modeling": "modelling", "modeled": "modelled", "channeling": "channelling",
    "channeled": "channelled", "labeled": "labelled", "labeling": "labelling",
    "leveled": "levelled", "leveling": "levelling", "traveling": "travelling",
    "traveled": "travelled", "signaled": "signalled", "signaling": "signalling",
    "canceled": "cancelled", "canceling": "cancelling", "fueled": "fuelled",
    "judgment": "judgement", "judgments": "judgements", "toward": "towards",
    "artifact": "artefact", "artifacts": "artefacts", "aging": "ageing",
    "aluminum": "aluminium", "defense": "defence", "story": "storey (if a floor)",
    "stories": "storeys (if floors)",
}
TERM_FIXES = {
    "fabric": "layout", "stand-off": "standoff", "stand off": "standoff",
    "set-up": "setup (noun) / set up (verb)",
}
FIRST_PERSON = re.compile(r"\b(I|we|We|our|Our|us|my|My|ours|myself|ourselves)\b")
CONTRACTION = re.compile(r"\b\w+(n't|'re|'ve|'ll|'d|'m)\b|\b(it's|that's|there's|here's|what's|let's)\b", re.I)
INTENSIFIERS = re.compile(r"\b(very|extremely|dramatically|huge|hugely|clearly|obviously|remarkably|"
                          r"a lot|lots of|incredibly|massive|massively|tremendous|tremendously|"
                          r"really|quite|surprisingly|interestingly|of course|basically|totally|"
                          r"absolutely|enormous|enormously|striking|strikingly)\b", re.I)
INFORMAL_START = re.compile(r"(?:^|[.!?]\s+)(So|But|And|Also|Plus|Anyway|Well),?\s")
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?\w+(ed|en|wn|lt|pt|ght|un|ung|ade|one|ept)\b", re.I)
PAST = re.compile(r"\b(was|were|had|did)\b|\b\w+ed\b", re.I)
PRESENT = re.compile(r"\b(is|are|has|have|does|do)\b", re.I)

# ---------------------------------------------------------------- latex masking
MATH_ENVS = r"equation|equation\*|align|align\*|gather|gather\*|multline|multline\*|eqnarray|eqnarray\*|displaymath|math"
SKIP_ENVS = MATH_ENVS + r"|tabular|tabular\*|tabularx|longtable|verbatim|lstlisting|tikzpicture"
ARG_CMDS = (r"label|ref|eqref|autoref|cref|Cref|pageref|cite|citep|citet|textcite|parencite|"
            r"autocite|citeauthor|citeyear|input|include|includegraphics|url|href|addbibresource|"
            r"bibliography|begin|end|usepackage|ac|acp|acs|acl|acf|acsp|aclp|acfp|Ac|Acp|Acl|Acf|"
            r"acused|acro|hspace|vspace|setlength|newcommand|renewcommand|SI|si|num|unit")


def strip_comment(line):
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2]); i += 2; continue
        if c == "%":
            break
        out.append(c); i += 1
    return "".join(out)


def blank(s):
    return re.sub(r"[^\n]", " ", s)


def mask_line(line):
    """Replace commands' arguments, math and command names by spaces, keeping columns."""
    s = line
    s = re.sub(r"\\(?:%s)\*?(\[[^\]]*\])*\{[^{}]*\}" % ARG_CMDS, lambda m: blank(m.group(0)), s)
    s = re.sub(r"\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)|\\\[.*?\\\]", lambda m: blank(m.group(0)), s)
    s = re.sub(r"\\[a-zA-Z]+\*?", lambda m: blank(m.group(0)), s)
    return s


# ---------------------------------------------------------------- helpers
FRONT_MATTER = re.compile(r"Title|Acknowledg|AcroNyms|ListSymbols", re.I)


def chapter_files(root, args):
    """The chapters the main .tex actually loads, in order. Drafts are never included."""
    if args:
        return [Path(a) if Path(a).is_absolute() else root / a for a in args]
    main = main_tex(root)
    files = []
    if main:
        body = "\n".join(strip_comment(l) for l in
                         main.read_text(encoding="utf-8", errors="replace").splitlines())
        for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", body):
            p = root / (name if name.endswith(".tex") else name + ".tex")
            if p.exists() and p.parent.name == "Content":
                files.append(p)
    if not files:
        files = sorted([p for p in (root / "Content").glob("*.tex")
                        if re.match(r"^\d+\.", p.name)
                        and not re.search(r"temp|_old|_new", p.name, re.I)],
                       key=lambda p: int(p.name.split(".")[0]))
    return files


def main_tex(root):
    for p in root.glob("*.tex"):
        if r"\documentclass" in p.read_text(encoding="utf-8", errors="replace"):
            return p
    return None


def bib_keys(root):
    main = main_tex(root)
    names = []
    if main:
        t = main.read_text(encoding="utf-8", errors="replace")
        names = re.findall(r"\\addbibresource\{([^}]+)\}", t) + \
            [n + (".bib" if not n.endswith(".bib") else "") for n in
             re.findall(r"\\bibliography\{([^}]+)\}", t)]
    keys = set()
    for n in names or ["bibliography.bib"]:
        p = root / n
        if p.exists():
            keys |= set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,",
                                   p.read_text(encoding="utf-8", errors="replace")))
    return keys, names


def acronyms(root):
    p = next(iter((root / "Content").glob("*AcroNyms*.tex")), None)
    acr = {}
    if p:
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\\acro\{([^}]+)\}(?:\[([^\]]*)\])?\{([^}]*)\}", t):
            acr[m.group(1)] = (m.group(2) or m.group(1), m.group(3))
    return acr


def sentences(text):
    t = re.sub(r"\b(et al|e\.g|i\.e|Fig|Eq|Eqs|Figs|Ref|No|vs|approx|cf)\.", r"\1", text)
    t = re.sub(r"\d\.\d", "0", t)
    parts = [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z\\(])", t.strip()) if x.strip()]
    return parts


# ---------------------------------------------------------------- main
def lint(root, files):
    findings = defaultdict(list)
    keys, bibnames = bib_keys(root)
    acr = acronyms(root)
    labels = defaultdict(list)
    refs = defaultdict(list)
    floats = []

    def add(rule, f, ln, text, hint="", col=None):
        text = text.strip() if col is None else text[max(0, col - 70):col + 90].strip()
        findings[rule].append({"file": f, "line": ln, "text": text[:200], "hint": hint})

    # full-thesis label / ref inventory (all chapters, so cross-chapter refs resolve)
    for p in chapter_files(root, []):
        for i, raw in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            line = strip_comment(raw)
            rel = str(p.relative_to(root))
            for m in re.finditer(r"\\label\{([^}]*)\}", line):
                labels[m.group(1)].append((rel, i))
            for m in re.finditer(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]*)\}", line):
                for k in m.group(1).split(","):
                    refs[k.strip()].append((rel, i))

    for p in files:
        rel = str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        front = bool(FRONT_MATTER.search(p.name))
        env_stack, para, para_start = [], [], None
        cur_float = None

        def flush_para():
            nonlocal para, para_start
            text = " ".join(para).strip()
            # a lead-in that ends with ':' introduces a list or an equation and is not a paragraph
            if text and not text.rstrip().endswith(":"):
                sents = sentences(text)
                words = len(text.split())
                if len(sents) < 2:
                    add("paragraph-too-short", rel, para_start, text,
                        f"{len(sents)} sentence(s): merge with a neighbouring paragraph")
                elif len(sents) > 12 or words > 260:
                    add("paragraph-too-long", rel, para_start, text[:120] + " ...",
                        f"{len(sents)} sentences, {words} words")
                for s in sents:
                    if len(s.split()) > 35:
                        add("long-sentence", rel, para_start, s,
                            f"{len(s.split())} words: consider splitting")
            para, para_start = [], None

        for i, raw in enumerate(lines, 1):
            line = strip_comment(raw)
            for m in re.finditer(r"\\begin\{([^}]+)\}", line):
                env = m.group(1)
                env_stack.append(env)
                if re.fullmatch(r"figure\*?|table\*?", env) and not front:
                    cur_float = {"env": env, "file": rel, "line": i, "caption": False,
                                 "labels": [], "cells": []}
            in_skip = any(re.fullmatch(SKIP_ENVS, e) for e in env_stack)
            in_float = cur_float is not None
            if cur_float is not None:
                if "\\caption" in line:
                    cur_float["caption"] = True
                cur_float["labels"] += re.findall(r"\\label\{([^}]*)\}", line)
                if any(re.fullmatch(r"tabular\*?|tabularx|longtable", e) for e in env_stack) and "&" in line:
                    for cell in line.split("&"):
                        c = re.sub(r"\\\\.*", "", cell)
                        if re.search(r"\d\s*~?\s*(m|kg|kPa|Pa|ms|s|MPa|kg-TNT)\b", c):
                            add("unit-in-table-cell", rel, i, cell, "put the unit in the column header")
            for m in re.finditer(r"\\end\{([^}]+)\}", line):
                env = m.group(1)
                if env_stack and env_stack[-1] == env:
                    env_stack.pop()
                if re.fullmatch(r"figure\*?|table\*?", env) and cur_float:
                    floats.append(cur_float); cur_float = None

            # ---- checks that apply anywhere outside comments
            for m in re.finditer(r"\\(?:cite|citep|citet|textcite|parencite|autocite|citeauthor|citeyear)\*?(?:\[[^\]]*\])*\{([^}]*)\}", line):
                for k in m.group(1).split(","):
                    k = k.strip()
                    if k and k not in keys:
                        add("cite-key-not-in-bib", rel, i, line,
                            f"key '{k}' not in {', '.join(bibnames)}", m.start())
            if "NEEDCITATION" in line:
                add("needcitation", rel, i, raw)
            for m in re.finditer(r"\\label\{([^}]*)\}", line):
                k = m.group(1)
                if " " in k:
                    add("label-has-space", rel, i, k)
                if not re.match(r"(sec|ssec|sssection|eq|fig|tab):", k):
                    add("label-prefix", rel, i, k, "allowed: sec ssec sssection eq fig tab")
            for m in re.finditer(r"\\(ref|eqref|autoref|cref|Cref)\{([^}]*)\}", line):
                k = m.group(2)
                if "NEEDCITATION" in k:
                    continue
                if k not in labels:
                    add("ref-undefined", rel, i, line, f"no \\label{{{k}}} in the chapters", m.start())
                if m.group(1) in ("ref", "eqref"):
                    before = line[:m.start()].rstrip("~ \t")
                    word = re.search(r"(Figures?|Fig\.|Tables?|Equations?|Eqs?\.|Sections?|Chapters?|"
                                     r"Appendi(x|ces)|and|to|,|-|--|–)$", before, re.I)
                    if not word:
                        add("ref-without-word", rel, i, line,
                            "write Figure~\\ref / Table~\\ref / Equation~\\eqref / Section~\\ref", m.start())
                    elif m.group(1) == "eqref" and not re.search(r"(Equations?|and|to|,|-|--|–)$", before):
                        add("eqref-without-Equation", rel, i, line, "use 'Equation~\\eqref{...}'", m.start())
            if re.search(r"\\(section|subsection|subsubsection|paragraph|caption)\*?(\[[^\]]*\])?\{[^}]*\\ac\{", line):
                add("ac-in-heading-or-caption", rel, i, raw, "use \\acs{} or \\acl{} here")

            # ---- prose-only checks (never on the title page, acronym and symbol lists)
            if front:
                continue
            if in_skip or re.match(r"\s*\\(section|subsection|subsubsection|caption|label|input|includegraphics|centering|item\b)", line):
                if re.match(r"\s*\\item\b", line) and not in_skip:
                    pass  # list items are prose for spelling purposes, handled below
                else:
                    if not line.strip() or not in_float:
                        flush_para()
                    if not re.match(r"\s*\\(caption|item\b)", line):
                        continue
            masked = mask_line(line)

            if ";" in masked:
                add("semicolon", rel, i, line, "split into two sentences or use a comma", masked.index(";"))
            for m in re.finditer(r"\b([A-Za-z]+(?:ize|izes|ized|izing|ization|izations|izer|izers))\b", masked):
                if m.group(1).lower() not in IZE_OK:
                    add("spelling-ize", rel, i, m.group(1), "-ise / -isation")
            for m in re.finditer(r"\b([A-Za-z]+yz(?:e|es|ed|ing|er|ers))\b", masked):
                add("spelling-yze", rel, i, m.group(1), "-yse")
            for m in re.finditer(r"\b[A-Za-z]+\b", masked):
                w = m.group(0); lw = w.lower()
                if lw in WORD_FIXES and not (lw == "meter" and re.search(r"(para|dia|peri|milli|centi|kilo)meter", masked, re.I)):
                    add("spelling-british", rel, i, w, WORD_FIXES[lw])
            for term, fix in TERM_FIXES.items():
                for m in re.finditer(r"\b%s\b" % re.escape(term), masked, re.I):
                    add("terminology", rel, i, m.group(0), fix)
            for m in FIRST_PERSON.finditer(masked):
                add("first-person", rel, i, line, f"'{m.group(0)}'", m.start())
            for m in CONTRACTION.finditer(masked):
                add("contraction", rel, i, line, f"'{m.group(0)}': write it out", m.start())
            for m in INTENSIFIERS.finditer(masked):
                add("intensifier", rel, i, line, f"'{m.group(0)}': remove or state the magnitude", m.start())
            for m in INFORMAL_START.finditer(masked):
                add("informal-connector", rel, i, line,
                    f"'{m.group(1)}' at sentence start: use However, / Accordingly, / In addition,", m.start(1))
            for m in re.finditer(r"\b(Figure|Fig\.|Table|Equation|Eq\.|Section)\s*~?\s*\(?\d+(\.\d+)?\)?", masked):
                add("hardcoded-reference", rel, i, m.group(0), "use \\ref / \\eqref")
            for key, (short, long_) in acr.items():
                ma = re.search(r"(?<![\\\w])%s(s)?\b" % re.escape(short), masked)
                if ma:
                    add("acronym-plain-text", rel, i, line,
                        f"'{short}' must be written \\ac{{{key}}}", ma.start())
                ml = re.search(re.escape(long_), masked, re.I) if long_ else None
                if ml:
                    add("acronym-long-form-plain", rel, i, line,
                        f"'{long_}': use \\acl{{{key}}} or \\ac{{{key}}}", ml.start())

            # paragraph accumulation (running prose only)
            if in_float or re.match(r"\s*\\", line) and not re.match(r"\s*\\(textit|textbf|emph|ac|acp|acs|acl|cite)", line):
                if not line.strip():
                    flush_para()
                continue
            if not line.strip():
                flush_para()
            else:
                if para_start is None:
                    para_start = i
                para.append(re.sub(r"\s+", " ", masked))
        flush_para()

    # ---- floats: caption, label, referenced
    for fl in floats:
        if fl["file"] not in [str(p.relative_to(root)) for p in files]:
            continue
        kind = fl["env"].rstrip("*")
        if not fl["caption"]:
            add("float-no-caption", fl["file"], fl["line"], kind)
        if not fl["labels"]:
            add("float-no-label", fl["file"], fl["line"], kind)
        for lb in fl["labels"]:
            if lb not in refs:
                add("float-not-referenced", fl["file"], fl["line"], lb, "refer to it in the text")

    # ---- duplicate labels (whole thesis)
    for k, locs in labels.items():
        if len(locs) > 1:
            findings["label-duplicate"].append({"file": locs[0][0], "line": locs[0][1], "text": k,
                                                "hint": "also at " + ", ".join(f"{f}:{l}" for f, l in locs[1:])})
    return findings


# ---------------------------------------------------------------- register profile
def prose_text(lines):
    """Running prose of a block of lines: no comments, environments, headings or math."""
    out, stack = [], []
    for raw in lines:
        line = strip_comment(raw)
        for m in re.finditer(r"\\begin\{([^}]+)\}", line):
            stack.append(m.group(1))
        skip = any(re.fullmatch(SKIP_ENVS + r"|figure\*?|table\*?", e) for e in stack)
        for m in re.finditer(r"\\end\{([^}]+)\}", line):
            if stack and stack[-1] == m.group(1):
                stack.pop()
        if skip or re.match(r"\s*\\(section|subsection|subsubsection|label|input|begin|end)", line):
            continue
        out.append(re.sub(r"\s+", " ", mask_line(line)))
    return " ".join(out)


def profile(text):
    sents = [s for s in sentences(text) if len(s.split()) > 2]
    if not sents:
        return None
    words = sum(len(s.split()) for s in sents)
    passive = sum(1 for s in sents if PASSIVE.search(s))
    past = sum(len(PAST.findall(s)) for s in sents)
    present = sum(len(PRESENT.findall(s)) for s in sents)
    return {
        "sentences": len(sents),
        "words_per_sentence": round(words / len(sents), 1),
        "passive_share": round(100 * passive / len(sents)),
        "past_share_of_tensed": round(100 * past / max(1, past + present)),
        "intensifiers_per_1000_words": round(1000 * len(INTENSIFIERS.findall(text)) / max(1, words), 1),
    }


def reference_block(root, files):
    """Lines of the register-reference section named in the thesis CLAUDE.md."""
    cm = root / "CLAUDE.md"
    if not cm.exists():
        return None, None
    m = re.search(r"Register reference:\s*`([^`]+)`", cm.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None, None
    label = m.group(1)
    levels = {"section": 1, "subsection": 2, "subsubsection": 3}
    for p in files:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, l in enumerate(lines):
            if "\\label{%s}" % label in l:
                h = re.search(r"\\(section|subsection|subsubsection)\{", l)
                lvl = levels[h.group(1)] if h else 2
                end = len(lines)
                for j in range(i + 1, len(lines)):
                    hh = re.match(r"\s*\\(section|subsection|subsubsection)\{", lines[j])
                    if hh and levels[hh.group(1)] <= lvl:
                        end = j
                        break
                return label, lines[i:end]
    return label, None


def register_report(root, files):
    label, block = reference_block(root, chapter_files(root, []))
    ref = profile(prose_text(block)) if block else None
    rows = []
    for p in files:
        if FRONT_MATTER.search(p.name):
            continue
        pr = profile(prose_text(p.read_text(encoding="utf-8", errors="replace").splitlines()))
        if not pr:
            continue
        flags = []
        if pr["sentences"] < 15:
            flags.append("too short to compare")
        elif ref:
            if abs(pr["words_per_sentence"] - ref["words_per_sentence"]) > 0.3 * ref["words_per_sentence"]:
                flags.append("sentence length")
            # the rules ask for frequent passive voice: only a share well below the reference is a drift
            if pr["passive_share"] < ref["passive_share"] - 15:
                flags.append("less passive")
            if pr["intensifiers_per_1000_words"] > ref["intensifiers_per_1000_words"] + 2:
                flags.append("intensifiers")
        rows.append({"file": p.name, **pr, "differs_from_reference": flags})
    return {"reference": label, "reference_profile": ref, "chapters": rows}


# ---------------------------------------------------------------- register card
def register_card(root):
    """A short, reusable description of the reference voice, so reviewers need not read the section."""
    files = chapter_files(root, [])
    label, block = reference_block(root, files)
    if not block:
        return None
    text = prose_text(block)
    prof = profile(text)
    # exemplars come from readable text: citations dropped, math and spacing kept legible
    readable = []
    stack = []
    for raw in block:
        line = strip_comment(raw)
        for m in re.finditer(r"\\begin\{([^}]+)\}", line):
            stack.append(m.group(1))
        skip = any(re.fullmatch(SKIP_ENVS + r"|figure\*?|table\*?", e) for e in stack)
        for m in re.finditer(r"\\end\{([^}]+)\}", line):
            if stack and stack[-1] == m.group(1):
                stack.pop()
        if skip or re.match(r"\s*\\(section|subsection|subsubsection|label|begin|end)", line):
            continue
        line = re.sub(r"\s*~?\\cite[a-z]*\{[^}]*\}", "", line)
        line = re.sub(r"\\(?:ref|eqref)\{[^}]*\}", "X", line)
        line = re.sub(r"\\ac[a-z]*\{([^}]*)\}", r"\1", line)
        line = re.sub(r"\$([^$]*)\$", r"\1", line).replace("~", " ").replace("--", "-")
        line = re.sub(r"\\[a-zA-Z]+\*?(\{([^}]*)\})?", r"\2", line)
        readable.append(line)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", " ".join(readable))
             if 12 <= len(s.split()) <= 32]
    groups = [
        [s for s in sents if PASSIVE.search(s)],
        [s for s in sents if re.match(r"(However|Accordingly|In consequence|Nor|Such|This|These)\b", s)],
        [s for s in sents if re.search(r"\bet al\b|\b[A-Z][a-z]+ and [A-Z][a-z]+\b", s)],
        sents,
    ]
    picks = []
    for g in groups:  # two from each kind, then fill to eight
        for s in g:
            if s not in picks and (sum(1 for p in picks if p in g) < 2 or g is sents):
                picks.append(s)
            if len(picks) >= 8 or (g is not sents and sum(1 for p in picks if p in g) >= 2):
                break
    rules = []
    cm = (root / "CLAUDE.md").read_text(encoding="utf-8", errors="replace")
    for line in cm.splitlines():
        if line.startswith("- Register") or line.startswith("- Tone") or line.startswith("- Voice"):
            rules.append(line)
    stamp = max(p.stat().st_mtime for p in files) if files else 0
    card = [f"# Register card ({label})", "",
            "Generated by lint.py --card from the reference section. Regenerate after editing that section.",
            f"<!-- source-mtime {stamp:.0f} -->", "", "## Rules (from CLAUDE.md)", *rules, "",
            "## Profile of the reference",
            f"- {prof['words_per_sentence']} words per sentence, {prof['passive_share']}% of sentences passive, "
            f"{prof['past_share_of_tensed']}% past among tensed verbs, "
            f"{prof['intensifiers_per_1000_words']} intensifiers per 1000 words", "",
            "## Exemplar sentences (the voice to match)", *[f"- {s}" for s in picks]]
    out = root / ".claude" / "cache" / "register_card.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(card) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- definitions index
def definitions(root):
    """First appearance (file:line) of each listed symbol, each acronym and each emphasised term."""
    files = chapter_files(root, [])
    sym_file = next(iter((root / "Content").glob("*ListSymbols*.tex")), None)
    symbols = []
    if sym_file:
        symbols = sorted(set(re.findall(r"\$([^$]{1,40})\$",
                                        sym_file.read_text(encoding="utf-8", errors="replace"))), key=len, reverse=True)
    acr = acronyms(root)
    first = {}
    for p in files:
        if FRONT_MATTER.search(p.name):
            continue
        for i, raw in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            line = strip_comment(raw)
            loc = f"{p.name}:{i}"
            for m in re.finditer(r"\\(?:emph|textit)\{([^{}]{3,60})\}", line):
                first.setdefault("term: " + m.group(1).strip().lower(), loc)
            for m in re.finditer(r"\b(?:termed|referred to as|is defined as|are defined as|denoted)\s+(?:the\s+)?([a-z][a-z\- ]{2,40}?)(?=[,.)]|\s\\|\s\$)", line):
                first.setdefault("term: " + m.group(1).strip(), loc)
            for m in re.finditer(r"\\ac[a-z]*\{([^}]+)\}", line):
                if m.group(1) in acr:
                    first.setdefault("acronym: " + m.group(1), loc)
            if "$" in line:
                segs = [x.strip() for x in re.findall(r"\$([^$]+)\$", line)]
                for s in symbols:
                    key = "symbol: $" + s + "$"
                    if key in first:
                        continue
                    pat = r"(?<![A-Za-z\\_^])" + re.escape(s.strip()) + r"(?![A-Za-z])"
                    if any(seg == s.strip() or re.search(pat, seg) for seg in segs):
                        first[key] = loc
    return first


SEVERITY = {
    "label-duplicate": "error", "ref-undefined": "error", "cite-key-not-in-bib": "error",
    "float-no-caption": "error", "float-no-label": "error",
    "semicolon": "rule", "spelling-ize": "rule", "spelling-yze": "rule", "spelling-british": "rule",
    "first-person": "rule", "acronym-plain-text": "rule", "acronym-long-form-plain": "rule",
    "ac-in-heading-or-caption": "rule", "ref-without-word": "rule", "eqref-without-Equation": "rule",
    "hardcoded-reference": "rule", "label-has-space": "rule", "label-prefix": "rule",
    "terminology": "rule", "unit-in-table-cell": "rule", "float-not-referenced": "rule",
    "contraction": "rule", "informal-connector": "rule", "intensifier": "check",
    "paragraph-too-short": "check", "paragraph-too-long": "check", "long-sentence": "check",
    "needcitation": "info",
}


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    as_json = "--json" in argv
    args = [a for a in argv[1:] if a not in ("--json", "--card")]
    if not args:
        print(__doc__); return 2
    root = Path(args[0]).resolve()
    if "--card" in argv:
        out = register_card(root)
        print(f"register card written: {out}" if out else "no register reference found in CLAUDE.md")
        return 0
    files = chapter_files(root, args[1:])
    f = lint(root, files)
    reg = register_report(root, files)
    if as_json:
        print(json.dumps({"files": [str(p.relative_to(root)) for p in files], "findings": f,
                          "register": reg, "definitions": definitions(root)},
                         ensure_ascii=False, indent=1))
        return 0
    order = ["error", "rule", "check", "info"]
    print(f"Checked {len(files)} file(s): " + ", ".join(p.name for p in files))
    for sev in order:
        rules = [r for r in f if SEVERITY.get(r, "rule") == sev]
        if not rules:
            continue
        print(f"\n## {sev.upper()}")
        for r in sorted(rules):
            print(f"\n### {r} ({len(f[r])})")
            for x in f[r]:
                hint = f"  -> {x['hint']}" if x["hint"] else ""
                print(f"- {x['file']}:{x['line']}  {x['text']}{hint}")
    print("\n## REGISTER PROFILE")
    if reg["reference_profile"]:
        r = reg["reference_profile"]
        print(f"reference {reg['reference']}: {r['words_per_sentence']} words/sentence, "
              f"{r['passive_share']}% passive, {r['past_share_of_tensed']}% past, "
              f"{r['intensifiers_per_1000_words']} intensifiers/1000 words")
    else:
        print("no register reference found in CLAUDE.md ('Register reference: `label`')")
    for c in reg["chapters"]:
        flag = ("  <- differs: " + ", ".join(c["differs_from_reference"])) if c["differs_from_reference"] else ""
        print(f"- {c['file']}: {c['words_per_sentence']} w/s, {c['passive_share']}% passive, "
              f"{c['past_share_of_tensed']}% past, {c['intensifiers_per_1000_words']} int/1000{flag}")
    print("\nSummary: " + ", ".join(f"{r}={len(v)}" for r, v in sorted(f.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
