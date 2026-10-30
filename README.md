# Novel kit (reusable across projects; configured by novel.json)
New project: `./init.sh ~/mynovel "Title"` then fill novel.json (Inkstone id, repo, limits), canon/bible.md (rules), glossary.json (banned/preferred words, filler list), names.txt (spellcheck names).
Per chapter:
1. `cp plans/_template.md plans/chN.md` and fill it (purpose, REQUIRED cost line, who-learns-what, numbers, 5 scene budgets, hook).
2. `python3 tools/ctx.py N` -> compact brief (~3-4k tokens). Draft chN.md in one pass; patch with Edit.
3. `python3 tools/check3.py chN.md plans/chN.md --strict` (exit 1 on failure; words, British, glossary, filler, cost plan; advisory: repeats, openers, thought tags).
4. Canon: `echo "- bullets" | python3 tools/facts_add.py N "Title" "POV"` (max 120 words), `python3 tools/ledger_add.py N QR LEVEL CE_BEFORE CE_DELTA note`; update characters/knowledge/threads/timeline.
5. Publish a Part: `tools/pub.sh FIRST LAST SRC_DIR REPO_DIR` (strict gate, convert, push) then run the printed snippets: `inkstone.py helpers`, `inkstone.py publish A B`, `inkstone.py wait` until done:true.
6. Fix a published chapter: edit md, `pub.sh`-style convert+push, then `inkstone.py edit N` (needs canon/ids.json; refresh with `inkstone.py ids` + `ids_save.py`).
Rules of thumb: fresh session per Part; continuity checks via subagent returning contradictions only; never delete the temp branch unless asked.
