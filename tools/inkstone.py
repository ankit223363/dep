#!/usr/bin/env python3
"""Generates browser snippets for Inkstone (run them with the built-in browser's javascript tool).
  inkstone.py helpers            -> defines window.__ink (run once per page load, on the novel page)
  inkstone.py publish A B        -> background loop publishing chapters A..B (60s CDN wait)
  inkstone.py wait               -> poll snippet (waits 40s, returns log/done); repeat until done:true
  inkstone.py ids                -> collects chapter ids across list pages into window.__ids (returns JSON {n:id}); save via ids_save.py
  inkstone.py edit N             -> prints the edit-page URL (from canon/ids.json) and the save snippet (run after navigating)"""
import json, sys
sys.path.insert(0, __import__("os").path.dirname(__file__)); import nk
c = nk.cfg(); a = sys.argv[1:]
if not a: sys.exit(__doc__)
HELP = """const B='%s';const I=window.__ink={sleep:ms=>new Promise(r=>setTimeout(r,ms)),btn:t=>[...document.querySelectorAll('button')].find(b=>b.textContent.trim().toLowerCase()===t),async get(n){const x=await fetch(B+'ch'+String(n).padStart(2,'0')+'.json?v='+Date.now(),{cache:'no-store'});if(!x.ok)throw new Error('fetch '+n+' '+x.status);return x.json();},async fill(c){const i=document.querySelector('input[placeholder="Title Here"]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,c.title);i.dispatchEvent(new Event('input',{bubbles:true}));const ed=tinymce.editors[0];ed.setContent(c.html);ed.undoManager.add();ed.fire('change');ed.fire('input');await I.sleep(700);return i;},async save(n){const c=await I.get(n);await I.sleep(1500);const i=await I.fill(c);[...document.querySelectorAll('*')].find(e=>e.children.length===0&&e.textContent.trim().toLowerCase()==='update').click();await I.sleep(2500);return {n,saved:/saved/i.test(document.body.innerText),title:i.value,words:(document.body.innerText.match(/[\\d,]+ words/g)||[])[0]};},async publishNew(n){const c=await I.get(n);[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='CREATE CHAPTER').click();await I.sleep(2500);await I.fill(c);I.btn('publish').click();await I.sleep(1800);I.btn('confirm').click();await I.sleep(2500);const nn=I.btn('not now');if(nn)nn.click();await I.sleep(2500);return {n};}};'ready'""" % c["raw_base"]
cmd = a[0]
if cmd == "helpers": print(HELP)
elif cmd == "publish":
    ns = list(range(int(a[1]), int(a[2]) + 1))
    print("window.__log=[];window.__done=false;(async()=>{await window.__ink.sleep(60000);for(const n of %s){try{await window.__ink.publishNew(n);window.__log.push('ok '+n)}catch(e){window.__log.push('err '+n+' '+e);break}}window.__done=true})();'started'" % json.dumps(ns))
elif cmd == "wait": print("await window.__ink.sleep(40000);({log:window.__log,done:window.__done})")
elif cmd == "ids":
    print("""window.__ids={};(async()=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const pages=[...document.querySelectorAll('li,button')].filter(e=>/^\\d+$/.test(e.textContent.trim())).map(e=>e.textContent.trim());for(const p of [...new Set(pages)]){[...document.querySelectorAll('li,button')].find(e=>e.textContent.trim()===p).click();await sl(2000);document.querySelectorAll('a[href*="/chapter/edit/"]').forEach(a=>{const m=a.textContent.match(/^0*(\\d+)/);if(m)window.__ids[m[1]]=a.getAttribute('href').split('/').pop()})}window.__idsDone=true})();'collecting; wait 20s then run: JSON.stringify(window.__ids)'""")
elif cmd == "edit":
    n = a[1]; ids = json.loads((nk.root()/"canon"/"ids.json").read_text())
    if n not in ids: sys.exit(f"no id for ch{n}; run `inkstone.py ids` and save with ids_save.py")
    print("NAVIGATE:", f"https://inkstone.webnovel.com/novels/chapter/edit/{c['inkstone_novel_id']}/{ids[n]}")
    print("THEN RUN (wait ~60s after pushing JSON first):")
    print(HELP.replace("'ready'", "") + "await new Promise(r=>setTimeout(r,3000));await window.__ink.save(%s)" % n)
