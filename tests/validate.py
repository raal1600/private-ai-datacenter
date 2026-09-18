"""Offline structural regression checks; standard library only."""
from pathlib import Path
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'index.html').read_text();raw=re.search(r'<script[^>]*id="architecture-data"[^>]*>(.*?)</script>',s,re.S)[1];data=json.loads(raw);checks=[]
def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
check('18 ordered views',[d['id'] for d in data['diagrams']]==[f'{i:02d}' for i in range(1,19)])
check('No external runtime script',not re.search(r'<script[^>]+src=',s))
check('CSP denies connections',"connect-src 'none'" in s)
check('Dark color scheme','color-scheme:dark' in s)
check('Mobile menu and skip link','id="menuToggle"' in s and 'class="skip-link"' in s)
check('Identical entrypoints',(ROOT/'architecture.html').read_text()==s)
for d in data['diagrams']:
 check(d['id']+': source matches',d['code']==(ROOT/'diagrams'/d['file']).read_text())
 try:ET.fromstring(d['svg']);valid=True
 except ET.ParseError:valid=False
 check(d['id']+': valid SVG XML',valid)
 check(d['id']+': dark Mermaid','theme: dark' in d['code'])
 check(d['id']+': references resolve',all(k in data['sources'] for k in d['refs']))
 check(d['id']+': related views resolve',all(any(v['id']==i for v in data['diagrams']) for i in d['related']))
result={'checks':len(checks),'passed':sum(c['passed'] for c in checks),'results':checks}
(ROOT/'docs/validation-static.json').write_text(json.dumps(result,indent=2)+'\n');print(f"Static: {result['passed']}/{result['checks']} passed")
sys.exit(0 if all(c['passed'] for c in checks) else 1)
