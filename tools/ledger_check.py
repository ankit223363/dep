#!/usr/bin/env python3
"""Checks canon/ledger.csv: ce_before + ce_delta == ce_after; QR never decreases; CE <= 400."""
import csv, sys
from pathlib import Path
rows = list(csv.DictReader(open(Path(__file__).parent.parent/"canon"/"ledger.csv")))
bad = 0; qr = 0
for r in rows:
    q = int(r["qr"] or 0)
    if q < qr: print("QR decreased at ch", r["chapter"]); bad += 1
    qr = max(qr, q)
    if r["ce_before"] and r["ce_delta"] and r["ce_after"]:
        if int(r["ce_before"]) + int(r["ce_delta"]) != int(r["ce_after"]):
            print("CE arithmetic wrong at ch", r["chapter"]); bad += 1
    if r["ce_after"] and int(r["ce_after"]) > 400: print("CE>400 at ch", r["chapter"]); bad += 1
print("ledger ok" if not bad else f"{bad} problem(s)"); sys.exit(1 if bad else 0)
