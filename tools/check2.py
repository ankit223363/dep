import re, sys
from spellchecker import SpellChecker

import os
WHITELIST = set()
_p = os.path.join(os.environ.get("NOVEL_ROOT", "."), "canon", "names.txt")
if os.path.exists(_p): WHITELIST |= set(open(_p).read().split())
BRIT = r"\b(colou?r(?<!color)|colour\w*|grey\w*|realis\w*|recognis\w*|organis\w*|apologis\w*|metre\w*|centre\w*|defence|offence|travell\w*|favour\w*|honour\w*|armour\w*|neighbour\w*|behaviour\w*|labour\w*|harbour\w*|plough\w*|towards|amongst|whilst|learnt|spelt|dreamt|programme|cheque|tyre|kerb|mould\w*|smoulder\w*|sceptic\w*|jewellery|analys(e|ed|ing)|paralys(e|ed|ing))\b"

text = open(sys.argv[1]).read()
body = re.sub(r"```.*?```", " ", text, flags=re.S)
words = re.findall(r"[A-Za-z][A-Za-z'\-]*", text)
print("WORDS:", len(text.split()))

sp = SpellChecker()
cand = set()
for w in re.findall(r"[A-Za-z][A-Za-z']*", body):
    lw = w.lower().strip("'")
    if lw.endswith("'s"): lw2 = lw[:-2]
    else: lw2 = lw
    if lw in WHITELIST or lw2 in WHITELIST: continue
    if w[0].isupper() and w.lower() not in sp: continue  # proper nouns
    if sp.unknown([lw2]): cand.add(lw)
print("SPELL?:", sorted(cand))
print("BRITISH:", sorted(set(m.group(0) for m in re.finditer(BRIT, body, re.I))))

# tense heuristic: narration (outside quotes/italics) with past-tense markers
issues = []
for para in body.split("\n"):
    nar = re.sub(r'"[^"]*"', "", para)
    nar = re.sub(r"\*[^*]+\*", "", nar)
    for s in re.split(r"(?<=[.!?])\s+", nar):
        if re.search(r"\b(was|were|had|did)\b", s) and not re.search(r"\b(has|have|is|are|will|would|years ago|ago|before|once|when he was|since)\b", s):
            issues.append(s.strip()[:140])
print("TENSE-CHECK (%d):" % len(issues))
for i in issues: print("  -", i)
