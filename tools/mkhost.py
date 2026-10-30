#!/usr/bin/env python3
"""Convert chNN.md files into Inkstone-ready JSON ({n,title,html}) for hosting.

Usage: mkhost.py SRC_DIR OUT_DIR [LO HI]
Rules (same as the manual template): only <p> paragraphs; *x* -> <em>,
**x** -> <strong>; '* * *' scene break -> <p>* * *</p>; ``` panels ->
<p>```<br />line<br />```</p>; '#'/'##' heading lines dropped, title taken
from '## Chapter N - Title'.
"""
import html
import json
import re
import sys
from pathlib import Path


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def convert(text: str):
    title = None
    out, code = [], None
    for ln in text.split("\n"):
        ln = ln.rstrip("\r")
        m = re.match(r"^##\s+(Chapter\s+\d+\s*[–-]\s*.+)$", ln)
        if m:
            title = m.group(1).replace(" - ", " – ", 1)
            continue
        if ln.startswith("# "):
            continue
        if ln.strip() == "```":
            if code is None:
                code = []
            else:
                body = "<br />".join(html.escape(c, quote=False) for c in code)
                out.append("<p>```<br />" + body + "<br />```</p>")
                code = None
            continue
        if code is not None:
            code.append(ln)
            continue
        if not ln.strip():
            continue
        if ln.strip() == "* * *":
            out.append("<p>* * *</p>")
            continue
        out.append("<p>" + inline(ln) + "</p>")
    return title, "\n".join(out)


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    hi = int(sys.argv[4]) if len(sys.argv) > 4 else 999
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("ch[0-9][0-9].md")):
        n = int(f.stem[2:])
        if not lo <= n <= hi:
            continue
        title, body = convert(f.read_text(encoding="utf-8"))
        if not title:
            sys.exit(f"{f}: no '## Chapter N - Title' line")
        (dst / f"ch{n:02d}.json").write_text(
            json.dumps({"n": n, "title": title, "html": body}, ensure_ascii=False),
            encoding="utf-8",
        )
        print(n, title, len(body))


if __name__ == "__main__":
    main()
