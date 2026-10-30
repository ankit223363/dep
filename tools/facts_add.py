#!/usr/bin/env python3
"""Usage: facts_add.py N "Title" "POV" < text   (stdin = bullet facts). Rejects entries over facts_max_words, appends to canon/facts/current.md."""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__)); import nk
n, title, pov = sys.argv[1:4]; body = sys.stdin.read().strip(); mx = nk.cfg()["facts_max_words"]
w = len(body.split())
if w > mx: sys.exit(f"facts too long: {w} words (max {mx}); condense")
p = nk.root()/"canon"/"facts"/"current.md"
with open(p, "a") as f: f.write(f"\n## ch{n} {title} ({pov})\n{body}\n")
print("appended", w, "words")
