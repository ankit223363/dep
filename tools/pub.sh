#!/usr/bin/env bash
# Usage: tools/pub.sh FIRST LAST SRC_DIR REPO_DIR
# STRICT gate (words, British, glossary, filler, cost plan) -> ledger check -> convert -> commit -> push (sets upstream) -> prints Inkstone snippets.
# Never deletes the branch. Chapters are public while it exists.
set -euo pipefail
K="$(cd "$(dirname "$0")/.." && pwd)"; export NOVEL_ROOT="$K"
A=$1; B=$2; SRC=$3; REPO=$4; BR=$(python3 -c "import sys;sys.path.insert(0,'$K/tools');import nk;print(nk.cfg()['branch'])")
for n in $(seq "$A" "$B"); do
  f="$SRC/ch$n.md"; [ -f "$f" ] || { echo "missing $f"; exit 1; }
  p="$K/plans/ch$n.md"
  python3 "$K/tools/check3.py" "$f" $( [ -f "$p" ] && echo "$p" ) --strict | grep -E "STRICT|MISSING" | sed "s/^/ch$n: /" || { echo "ch$n failed the strict gate; run check3.py to see why"; exit 1; }
done
python3 "$K/tools/ledger_check.py"
tmp=$(mktemp -d); for n in $(seq "$A" "$B"); do cp "$SRC/ch$n.md" "$tmp/"; done
python3 -I "$K/tools/mkhost.py" "$tmp" "$REPO/chapters"
cd "$REPO"; git checkout "$BR" 2>/dev/null || git checkout -b "$BR"
git add chapters && git commit -qm "Add chapters $A-$B" && git push -q -u origin "$BR"
git config --add remote.origin.fetch "+refs/heads/$BR:refs/remotes/origin/$BR" 2>/dev/null || true
SHA=$(git rev-parse HEAD)
echo "Pushed commit $SHA. Use NK_REF=$SHA before inkstone.py to bypass the raw-CDN cache (branch URLs stay cached ~5+ min)."
echo "Next in the Inkstone novel page (javascript tool):"
echo "1) python3 $K/tools/inkstone.py helpers   (once per page load)"
echo "2) python3 $K/tools/inkstone.py publish $A $B"
echo "3) python3 $K/tools/inkstone.py wait       (repeat until done:true)"
