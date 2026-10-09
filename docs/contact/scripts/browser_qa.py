from playwright.sync_api import sync_playwright
import json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1300,'height':900});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8788/');page.wait_for_function("!document.querySelector('#run').disabled",timeout=120000)
 page.screenshot(path=str(R/'results/browser-ready.png'))
 results=[]
 for case in ['nominal','low-friction','heavy']:
  page.select_option('#case',case);page.click('#run');page.wait_for_function("document.querySelector('#status').textContent.startsWith('Finished')",timeout=120000)
  results.append({'case':case,'status':page.locator('#status').inner_text(),'result':page.locator('#result').inner_text()})
  page.screenshot(path=str(R/f'results/browser-{case}.png'))
 page.click('#run');page.click('#pause');paused=page.locator('#time').inner_text();page.wait_for_timeout(250);assert page.locator('#time').inner_text()==paused
 page.click('#pause');page.wait_for_timeout(100);page.click('#reset');assert page.locator('#time').inner_text()=='0.00 s'
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(R/'results/browser-mobile.png'))
 assert not errors,errors
 (R/'results/browser-qa.json').write_text(json.dumps({'browser':'Playwright Chromium headless, software WebGL','pass':True,'cases':results,'pause_resume_reset':True,'mobile_layout':True,'page_errors':errors},indent=2));print(results)
 browser.close()
