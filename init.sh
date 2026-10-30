#!/usr/bin/env bash
# Usage: ./init.sh NEW_DIR "Novel Title"  -> scaffolds a new novel project from this kit (tools + empty canon).
set -e; K="$(cd "$(dirname "$0")" && pwd)"; D=$1; mkdir -p "$D"/{canon/facts,plans,tools}
find "$K/tools" -maxdepth 1 -type f -exec cp {} "$D/tools/" \; ; cp "$K/plans/_template.md" "$D/plans/"; cp "$K/canon/glossary.json" "$D/canon/"
echo '{}' > "$D/canon/ids.json"; : > "$D/canon/names.txt"; echo 'chapter,qr,level,ce_before,ce_delta,ce_after,note' > "$D/canon/ledger.csv"
for f in bible characters knowledge threads timeline; do printf "# %s (fill in)\n" "$f" > "$D/canon/$f.md"; done
cat > "$D/novel.json" <<J
{"title":"$2","inkstone_novel_id":"","repo":"OWNER/REPO","branch":"chapters-temp","raw_base":"https://raw.githubusercontent.com/OWNER/REPO/chapters-temp/chapters/","words_min":4000,"words_max":5000,"facts_max_words":120,"chapter_header":"# $2"}
J
cp "$K/README.md" "$D/README.md" 2>/dev/null || true; echo "Scaffolded $D. Edit novel.json, canon/*.md, glossary.json, names.txt (character names for spellcheck)."
