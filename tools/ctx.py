#!/usr/bin/env python3
"""Usage: python3 ctx.py N  -> prints the compact drafting brief for chapter N (about 3-4k tokens):
bible + characters + knowledge + threads + facts of the last 2 chapters + plans/chN.md."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import nk
root = nk.root()
n = int(sys.argv[1])
for name in ["rulebook", "bible", "characters", "knowledge", "threads"]:
    print((root/"canon"/f"{name}.md").read_text().strip(), "\n")
facts = "\n".join(p.read_text() for p in sorted((root/"canon"/"facts").glob("*.md")))
blocks = re.split(r"(?m)^(?=## ch)", facts)
sel = [b for b in blocks if (m := re.match(r"## ch0?(\d+)", b)) and int(m.group(1)) in (n-1, n-2)]
print("# RECENT FACTS\n" + "".join(sel))
plan = root/"plans"/f"ch{n}.md"
print("# PLAN\n" + (plan.read_text() if plan.exists() else f"(missing: copy plans/_template.md to plans/ch{n}.md)"))
