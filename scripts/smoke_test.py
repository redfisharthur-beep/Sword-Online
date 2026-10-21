"""Browser smoke test. Build first; requires Python Playwright and Chromium."""
import json
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT/'public')))
Thread(target=server.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{server.server_port}/'
KEY = 'sword-online-remaster-v2'
errors = []
failed = []

def enter(page):
    page.goto(URL, wait_until='networkidle')
    page.locator('#guest-login').click()
    page.locator('#enter-world').click()
    assert page.locator('#game-ui').is_visible()

def saved(page):
    return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))', KEY)

def close(page):
    page.locator('#window-close').click()

try:
    for f in (ROOT/'public').rglob('*'):
        if f.is_file():
            with urlopen(URL+str(f.relative_to(ROOT/'public'))) as response:
                assert response.status == 200
                response.read()
    assert not (ROOT/'public/.git').exists()
    assert not (ROOT/'public/scripts').exists()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1440, 'height':900})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('requestfailed', lambda req: failed.append(req.url))
        page.goto(URL, wait_until='networkidle')
        page.screenshot(path='/tmp/sword-login.png')
        page.locator('#guest-login').click()
        page.locator('#new-character').click()
        page.locator('[data-race="仙靈"]').click()
        assert page.locator('.job-choice').count() == 1
        page.locator('#new-name').fill('<b>旅人')
        page.locator('#create-confirm').click()
        page.locator('#enter-world').click()
        assert saved(page)['equipment']['武器'] == '符咒'
        assert page.locator('.skill-slot').count() == 8
        rect = page.locator('#world').bounding_box()
        shell = page.locator('.game-shell').bounding_box()
        assert abs(rect['width']-shell['width']) < 1
        assert abs(rect['height']-shell['height']) < 1
        page.locator('[data-window="status"]').first.click()
        assert page.locator('#window-content strong').inner_text() == '<b>旅人'
        assert page.locator('#window-content strong b').count() == 0
        close(page)
        page.locator('[data-window="inventory"]').first.click()
        page.locator('[data-equip="麻布包裹"]').click()
        assert saved(page)['bagSlots'] == 16
        close(page)
        page.locator('[data-window="shop"]').click()
        gold = saved(page)['gold']
        page.locator('[data-buy="藥草"]').click()
        assert saved(page)['gold'] == gold-12
        close(page)
        page.locator('#map-button').click()
        page.locator('[data-zone="0"]').click()
        before = saved(page)['hp']
        page.mouse.click(rect['x']+rect['width']*.73,rect['y']+rect['height']*.58)
        page.keyboard.press('q')
        assert page.locator('#target-panel').is_hidden()
        assert saved(page)['hp'] == before
        page.locator('#sit-button').click()
        page.reload(wait_until='networkidle')
        page.locator('#guest-login').click(); page.locator('#enter-world').click()
        assert saved(page)['sitting'] is True
        assert page.locator('#sit-button').inner_text() == '起'
        assert page.locator('#radar-zone').inner_text() == '廣靈鎮'
        page.locator('[data-window="system"]').click()
        with page.expect_download() as download:
            page.locator('[data-action="export"]').click()
        data = json.loads(Path(download.value.path()).read_text())
        assert data['player']['name'] == '<b>旅人'
        original = saved(page)
        page.locator('#save-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"format":"invalid"}'})
        page.wait_for_function("document.querySelector('#toast').textContent.includes('無法讀取')")
        assert saved(page) == original
        data['player']['name'] = '還原旅人'
        page.once('dialog', lambda dialog: dialog.accept())
        page.locator('#save-file').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':json.dumps(data).encode()})
        page.wait_for_function("document.querySelector('#hud-name').textContent==='還原旅人'")
        assert saved(page)['name'] == '還原旅人'
        page.screenshot(path='/tmp/sword-game.png')
        # Exercise combat in the harbor with a fresh, healthy character.
        page.locator('#map-button').click(); page.locator('[data-zone="1"]').click()
        if saved(page)['sitting']: page.locator('#sit-button').click()
        rect = page.locator('#world').bounding_box()
        page.mouse.click(rect['x']+rect['width']*.73,rect['y']+rect['height']*.58)
        assert page.locator('#target-panel').is_visible()
        page.keyboard.press('1')
        assert saved(page)['mp'] < data['player']['mp']
        assert '造成' in page.locator('#combat-lines').inner_text()
        # Responsive layout and UI must remain operable on a narrow screen.
        page.set_viewport_size({'width':390,'height':844})
        page.locator('[data-window="guide"]').click()
        assert page.locator('#window-title').inner_text() == '港口嚮導'
        page.locator('[data-action="shop"]').click()
        assert page.locator('[data-buy="藥草"]').is_visible()
        close(page)
        page.screenshot(path='/tmp/sword-mobile.png')
        # Item effects and resurrection must persist without free/duplicate usage.
        import copy
        fixture = copy.deepcopy(data['player'])
        fixture.update(name='補給測試', hp=20, mp=10, sitting=False, gold=0, bagSlots=16)
        fixture['inventory'] = ['藥草', '靈泉水', '招魂號角']
        items = browser.new_page()
        items.on('pageerror', lambda e: errors.append(str(e)))
        items.add_init_script('localStorage.setItem('+json.dumps(KEY)+','+json.dumps(json.dumps(fixture))+')')
        enter(items)
        items.locator('[data-window="inventory"]').first.click()
        items.locator('[data-equip="藥草"]').click()
        assert saved(items)['hp'] == 80
        assert '藥草' not in saved(items)['inventory']
        items.locator('[data-equip="靈泉水"]').click()
        assert saved(items)['mp'] == 70
        close(items)
        items.locator('[data-window="shop"]').click()
        items.locator('[data-buy="藥草"]').click()
        assert saved(items)['gold'] == 0
        assert '藥草' not in saved(items)['inventory']
        items.close()
        fixture.update(dead=True, corpse=True, hp=0)
        dead = browser.new_page()
        dead.on('pageerror', lambda e: errors.append(str(e)))
        dead.add_init_script('localStorage.setItem('+json.dumps(KEY)+','+json.dumps(json.dumps(fixture))+')')
        enter(dead)
        dead.locator('[data-window="inventory"]').first.click()
        dead.locator('[data-equip="招魂號角"]').click()
        assert saved(dead)['dead'] is False
        assert saved(dead)['hp'] > 0
        assert '招魂號角' not in saved(dead)['inventory']
        dead.close()
        corrupt = browser.new_page()
        corrupt.on('pageerror', lambda e: errors.append(str(e)))
        corrupt.add_init_script('localStorage.setItem('+json.dumps(KEY)+',JSON.stringify({name:"broken",inventory:null}))')
        enter(corrupt)
        assert saved(corrupt)['name'] == '軒轅旅人'
        corrupt.close()
        assert not errors, errors
        assert not failed, failed
        browser.close()
    print('PASS: public assets, character creation, escaping, canvas sizing, bag expansion, shop, safe zone, combat, persistence, save export/import, mobile UI; no browser errors or failed requests.')
finally:
    server.shutdown()
    server.server_close()
