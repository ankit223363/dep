import json, os
from pathlib import Path
def root():
    p = Path(os.environ.get("NOVEL_ROOT", Path(__file__).resolve().parent.parent)); return p
def cfg(): return json.loads((root()/"novel.json").read_text())
