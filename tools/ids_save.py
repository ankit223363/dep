#!/usr/bin/env python3
"""Usage: echo '{"1":"id",...}' | ids_save.py   (merges into canon/ids.json)"""
import json, sys
sys.path.insert(0, __import__("os").path.dirname(__file__)); import nk
p = nk.root()/"canon"/"ids.json"; d = json.loads(p.read_text()); d.update(json.loads(sys.stdin.read())); p.write_text(json.dumps(d, sort_keys=True)); print(len(d), "ids saved")
