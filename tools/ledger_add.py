#!/usr/bin/env python3
"""Usage: ledger_add.py CH QR LEVEL CE_BEFORE CE_DELTA [note]  -> appends canon/ledger.csv with ce_after computed, then validates."""
import sys, subprocess
sys.path.insert(0, __import__("os").path.dirname(__file__)); import nk
a = sys.argv[1:]
if len(a) < 5: sys.exit(__doc__)
ch, qr, lv, b, d = a[:5]; note = " ".join(a[5:]).replace(",", ";")
after = int(b) + int(d)
with open(nk.root()/"canon"/"ledger.csv", "a") as f: f.write(f"{ch},{qr},{lv},{b},{d},{after},{note}\n")
print("added: CE", b, "->", after)
sys.exit(subprocess.call([sys.executable, str(nk.root()/"tools"/"ledger_check.py")]))
