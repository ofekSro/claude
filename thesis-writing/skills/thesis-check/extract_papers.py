#!/usr/bin/env python3
"""Extract the text of every PDF in the thesis Papers/ folder once, into a cache.

Usage:
    python extract_papers.py <thesis_root> [papers_dir]

Writes <thesis_root>/.claude/cache/papers/<pdf stem>.txt with "=== page N ===" markers,
and index.tsv (file, pages, first author, year guessed from the file name).
A PDF is re-extracted only when it is newer than its text. No model is involved,
so the agents that search the papers read these texts instead of extracting again.
"""
import re
import subprocess
import sys
from pathlib import Path


def extract(pdf, out):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf)
        out.write_text("".join(f"\n=== page {i + 1} ===\n" + p.get_text() for i, p in enumerate(doc)),
                       encoding="utf-8")
        return len(doc)
    except ImportError:
        pass
    try:
        from pypdf import PdfReader
        r = PdfReader(str(pdf))
        out.write_text("".join(f"\n=== page {i + 1} ===\n" + (p.extract_text() or "")
                               for i, p in enumerate(r.pages)), encoding="utf-8")
        return len(r.pages)
    except ImportError:
        pass
    raw = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True).stdout
    pages = raw.decode("utf-8", errors="replace").split("\f")
    out.write_text("".join(f"\n=== page {i + 1} ===\n" + p for i, p in enumerate(pages)), encoding="utf-8")
    return len(pages)


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(argv) < 2:
        print(__doc__); return 2
    root = Path(argv[1]).resolve()
    papers = Path(argv[2]) if len(argv) > 2 else root / "Papers"
    cache = root / ".claude" / "cache" / "papers"
    cache.mkdir(parents=True, exist_ok=True)
    rows, new, kept, failed = [], 0, 0, []
    for pdf in sorted(papers.glob("*.pdf")):
        out = cache / (pdf.stem + ".txt")
        try:
            if out.exists() and out.stat().st_mtime >= pdf.stat().st_mtime:
                n = out.read_text(encoding="utf-8", errors="replace").count("=== page ")
                kept += 1
            else:
                n = extract(pdf, out)
                new += 1
        except Exception as e:  # a broken or cloud-only PDF must not stop the rest
            failed.append(f"{pdf.name}: {e}")
            continue
        m = re.match(r"([A-Za-z\-]+)[_ -]+(?:et[_ ]al[_ ]*)?(\d{4})", pdf.stem)
        rows.append(f"{pdf.name}\t{n}\t{m.group(1) if m else ''}\t{m.group(2) if m else ''}")
    (cache / "index.tsv").write_text("file\tpages\tauthor\tyear\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"{cache}: {new} extracted, {kept} up to date, {len(failed)} failed")
    for f in failed:
        print("  failed:", f)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
