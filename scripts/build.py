#!/usr/bin/env python3
"""Assemble offline HTML, documentation and the minimal Pages artifact."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
def build():
    data=json.loads((ROOT/'content/architecture.json').read_text())
    manifest=json.loads((ROOT/'svg/manifest.json').read_text())
    assert [d['id'] for d in data['diagrams']]==[f'{i:02d}' for i in range(1,19)], 'Expected 18 ordered views'
    for d in data['diagrams']:
        source=ROOT/'diagrams'/d['file']
        assert source.parent==ROOT/'diagrams' and source.is_file(), 'Invalid source path'
        assert manifest[d['id']]==hashlib.sha256(source.read_bytes()).hexdigest(), f"Stale SVG: {d['id']}; run npm run render"
        d['code']=source.read_text();d['svg']=(ROOT/'svg'/f"{d['id']}.svg").read_text().replace('<br>','<br />')
        assert '<svg' in d['svg'] and '<script' not in d['svg'].lower(), 'Invalid SVG'
    text=(ROOT/'src/template.html').read_text()
    text=text.replace('/*__STYLES__*/',(ROOT/'src/base.css').read_text()+'\n'+(ROOT/'src/dark.css').read_text())
    text=text.replace('/*__DATA__*/',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    text=text.replace('/*__APP__*/',(ROOT/'src/app.js').read_text())
    for name in ['index.html','architecture.html']:(ROOT/name).write_text(text)
    (ROOT/'.nojekyll').touch()
    docs=['# Private AI Datacenter — detailed architecture','','[Open the explorer](https://raal1600.github.io/private-ai-datacenter/)','','Reference design, not deployed infrastructure.','']
    for d in data['diagrams']:
        docs += [f"## {d['id']} · {d['title']}",'',d['question'],'',d['summary'],'','```mermaid',d['code'].strip(),'```','','### Engineering notes','']
        docs += ['- '+n for n in d['notes']]+['','### References','']
        docs += [f"- [{data['sources'][k]['title']}]({data['sources'][k]['url']})" for k in d['refs']]+['']
    docs+=['## Assumptions','']
    for title,body in data['assumptions']:docs += ['### '+title,'',body,'']
    (ROOT/'docs').mkdir(exist_ok=True);(ROOT/'docs/architecture.md').write_text('\n'.join(docs)+'\n')
    site=ROOT/'_site';shutil.rmtree(site,ignore_errors=True);site.mkdir()
    for name in ['index.html','architecture.html','.nojekyll']:shutil.copy2(ROOT/name,site/name)
    for folder in ['diagrams','svg','docs']:shutil.copytree(ROOT/folder,site/folder)
    with zipfile.ZipFile(site/'private-ai-datacenter-offline.zip','w',zipfile.ZIP_DEFLATED,strict_timestamps=False) as z:
        for p in sorted(site.rglob('*')):
            if p.is_file() and p.suffix!='.zip':z.write(p,Path('private-ai-datacenter')/p.relative_to(site))
    print(f'Built 18 views; {len(text.encode()):,} bytes; self-contained HTML')
if __name__=='__main__':build()
