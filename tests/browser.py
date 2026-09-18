"""Exercise the standalone viewer in Chromium; no network is required to use it."""
from pathlib import Path
import json,os,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];checks=[]
def check(name,ok):
 checks.append({'name':name,'passed':bool(ok)})
 if not ok:print('FAIL:',name)
with sync_playwright() as p:
 args={'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_EXECUTABLE'):args['executable_path']=os.environ['CHROMIUM_EXECUTABLE']
 b=p.chromium.launch(**args);page=b.new_page(viewport={'width':1440,'height':1040},reduced_motion='reduce');errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.set_content((ROOT/'index.html').read_text())
 page.screenshot(path=str(ROOT/'docs/preview-desktop.png'))
 check('18 navigation items',page.locator('.navbtn').count()==18)
 check('Dark background',page.evaluate('getComputedStyle(document.body).backgroundColor')=='rgb(12, 16, 23)')
 for n in range(1,19):
  i=f'{n:02d}';page.evaluate('(id)=>architectureExplorer.selectView(id)',i)
  check(i+': SVG visible',page.locator('#stage svg').is_visible());page.locator('[data-tab="notes"]').click()
  check(i+': design notes',page.locator('.noterow').count()>0);page.locator('[data-tab="source"]').click()
  check(i+': Mermaid source',len(page.locator('#mermaidCode').input_value())>100)
 page.evaluate("architectureExplorer.selectView('01')");page.locator('#readSize').click();check('Read size',page.locator('#zoomLabel').inner_text()=='100%')
 page.locator('#zoomIn').click();check('Zoom in',page.locator('#zoomLabel').inner_text()=='125%');page.locator('#zoomOut').click();check('Zoom out',page.locator('#zoomLabel').inner_text()=='100%')
 page.locator('#fit').click();check('Fit',int(page.locator('#zoomLabel').inner_text().strip('%'))<100)
 with page.expect_download() as dl:page.locator('#downloadMmd').click()
 check('Mermaid download',dl.value.suggested_filename.endswith('.mmd'))
 with page.expect_download() as dl:page.locator('#exportSvg').click()
 check('SVG download',dl.value.suggested_filename.endswith('.svg'))
 page.locator('#navSearch').fill('zzzznomatchzzzz');check('Empty search',page.locator('.navbtn').count()==0)
 page.locator('#navSearch').fill('ESXi');check('Search matches',0<page.locator('.navbtn').count()<18);page.locator('#navSearch').fill('')
 page.locator('[data-section="hardware"]').click();check('Hardware section',page.locator('.infocard').count()>0);check('Weights calculation',page.locator('#outWeights').inner_text()=='335.5')
 page.locator('#params').fill('-1');check('Invalid input clears results',page.locator('#outWeights').inner_text()=='—');page.locator('#params').fill('671');check('Calculator recovers',page.locator('#outWeights').inner_text()=='335.5')
 page.locator('[data-section="catalog"]').click();check('Automation catalog',page.locator('tbody tr').count()>0)
 page.locator('[data-section="sources"]').click();check('Sources section',page.locator('.sourcerow').count()>0)
 page.evaluate("architectureExplorer.selectView('01')");check('Desktop no page overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 page.set_viewport_size({'width':390,'height':844});page.evaluate('syncNavigation()');page.screenshot(path=str(ROOT/'docs/preview-mobile.png'))
 check('Mobile menu visible',page.locator('#menuToggle').is_visible());check('Mobile sidebar collapsed',page.locator('#sidebar').evaluate('(el)=>el.inert'))
 page.locator('#menuToggle').click();check('Mobile menu opens',page.locator('#menuToggle').get_attribute('aria-expanded')=='true');check('Search focus',page.locator('#navSearch').evaluate('(el)=>document.activeElement===el'))
 page.keyboard.press('Escape');check('Escape closes menu',page.locator('#menuToggle').get_attribute('aria-expanded')=='false')
 page.locator('#menuToggle').click();page.locator('#nav [data-view="02"]').click();check('View selection closes menu',page.locator('#menuToggle').get_attribute('aria-expanded')=='false')
 check('Mobile no page overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));check('No JavaScript errors',not errors);check('No runtime network requests',not requests)
 result={'checks':len(checks),'passed':sum(c['passed'] for c in checks),'javascript_errors':errors,'network_requests':requests,'results':checks}
 (ROOT/'docs/validation-browser.json').write_text(json.dumps(result,indent=2)+'\n');print(f"Browser: {result['passed']}/{result['checks']} passed");b.close()
sys.exit(0 if all(c['passed'] for c in checks) else 1)
