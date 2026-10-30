#!/usr/bin/env python3
"""Usage: python3 check3.py chNN.md [plans/chNN.md]
Runs check2 (words, spelling, British, tense) then style checks:
glossary violations, filler density, repeated phrases, thought-tag frequency,
sentence-opener repetition, cost-ledger (plan file must name a cost)."""
import json, re, subprocess, sys, collections
from pathlib import Path
here = Path(__file__).parent
sys.path.insert(0, str(here)); import nk
strict = "--strict" in sys.argv; sys.argv = [a for a in sys.argv if a != "--strict"]
f = sys.argv[1]; fails = []
print(subprocess.run([sys.executable, str(here/"check2.py"), f], capture_output=True, text=True, env={**__import__("os").environ, "NOVEL_ROOT": str(nk.root())}).stdout.rstrip())
text = Path(f).read_text()
body = re.sub(r"```.*?```", " ", text, flags=re.S)
words = len(body.split())
g = json.loads((nk.root()/"canon"/"glossary.json").read_text())
print("\n-- GLOSSARY --")
bad = []
for w, fix in g["banned"].items():
    for m in re.finditer(r"\b%s\b" % w, body, re.I):
        ctx = body[max(0, m.start()-12):m.end()+12].replace("\n", " ")
        bad.append(f"'{w}' -> use '{fix}': ...{ctx}...")
print("\n".join(bad) or "ok"); fails += bad
print("-- RULE WARNINGS --")
rw = []
for pat, msg in g.get("warn_patterns", {}).items():
    for m in re.finditer(pat, body):
        rw.append(f"{msg}: ...{body[max(0,m.start()-20):m.end()+20]!r}")
print("\n".join(rw) or "ok"); fails += [r for r in rw if "filler" not in r]
print("\n-- FILLER (max %s per 1000 words each) --" % g["filler_max_per_1000"])
flag = False
for w in g["filler"]:
    n = len(re.findall(re.escape(w), body, re.I)); per = n*1000/max(words, 1)
    if per > g["filler_max_per_1000"]:
        flag = True; fails.append(w); print(f"  {w!r}: {n} ({per:.1f}/1000)")
print("ok" if not flag else "")
print("-- THOUGHT TAGS --")
th = len(re.findall(r"\b(he|she) thinks\b|\*\w[^*]*\*,? (he|she) thinks", body, re.I))
print(f"'thinks' tags: {th} ({th*1000/max(words,1):.1f}/1000; aim < 6)")
print("-- REPEATED PHRASES (5-word, >=3x) --")
toks = re.findall(r"[a-z']+", body.lower())
c = collections.Counter(" ".join(toks[i:i+5]) for i in range(len(toks)-4))
rep = [(p, n) for p, n in c.items() if n >= 3 and not re.search(r"^(the|a|and|of|to|in) ", p)]
for p, n in sorted(rep, key=lambda x: -x[1])[:12]: print(f"  {n}x {p}")
if not rep: print("ok")
print("-- SENTENCE OPENERS --")
sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", body)) if s.strip()]
op = collections.Counter(s.split()[0].lower().strip("\"*") for s in sents if s.split())
tot = len(sents)
for w, n in op.most_common(4): print(f"  {w}: {n} ({n*100/tot:.0f}%)" + ("  <- high" if n*100/tot > 12 else ""))
if len(sys.argv) > 2:
    print("\n-- COST LEDGER (plan) --")
    p = Path(sys.argv[2]).read_text()
    m = re.search(r"Cost of any advantage[^\n]*\n(.+?)(?=\nWho learns|\Z)", p, re.S)
    ok = bool(m and re.search(r"[A-Za-z]{4}", re.sub(r"^\s*(-|\d\.)\s*$", "", m.group(1))))
    print("ok: cost named" if ok else "MISSING: plan names no cost for the chapter's advantage")
    if not ok: fails.append("cost")

c = nk.cfg(); import re as _r
tw = len(text.split())
if tw < c["words_min"] or tw > c["words_max"]: fails.append("words %d" % tw)
if _r.search(r"\bBRITISH: \[.+\]", "") : pass
brit = subprocess.run([sys.executable, str(here/"check2.py"), f], capture_output=True, text=True, env={**__import__("os").environ, "NOVEL_ROOT": str(nk.root())}).stdout
if _r.search(r"BRITISH: \[.+\]", brit): fails.append("british")
print("\nSTRICT:", "FAIL " + ", ".join(map(str, fails)) if fails else "PASS")
if strict and fails: sys.exit(1)
