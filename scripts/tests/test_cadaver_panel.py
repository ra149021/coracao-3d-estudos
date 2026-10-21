"""Browser contract tests. Synthetic media proves UI, never anatomy."""
import functools
import http.server
import json
import shutil
import tempfile
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]


class CadaverPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='cadaver-panel-')
        self.root = Path(self.tmp.name)
        for name in ('cadaver-panel.js', 'cadaver-panel.css'):
            if (ROOT / 'site' / name).exists():
                shutil.copyfile(ROOT / 'site' / name, self.root / name)
        (self.root / 'assets').mkdir()
        # Visible handwriting-like fixture, explicitly not anatomical source media.
        (self.root / 'assets/fixture.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600"><rect width="900" height="600" fill="#dbc"/><text x="30" y="120" font-style="italic" font-size="50">Fixture anotada — não anatomia</text></svg>')
        self.manifest = {'version': 1, 'entries': [{'modelId': 'fixture-model', 'system': 'circulatory', 'partId': 'exact-id', 'label': 'Estrutura fixture', 'photoIds': ['original']}], 'photos': {'original': {'src': 'assets/fixture.svg', 'title': 'Original fixture', 'evidence': 'Mídia sintética; não valida anatomia.'}}}
        self.save_manifest()
        (self.root / 'index.html').write_text('<meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="cadaver-panel.css"><main id="host"></main><script type="module">import {mountCadaverPanel} from "./cadaver-panel.js";window.panel=mountCadaverPanel(document.querySelector("#host"));</script>')
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(self.root))
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.page = self.browser.new_page()
        self.page.set_default_timeout(4000)
        # Routing disables the browser HTTP cache; every subtest reads its fixture.
        self.page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:') else route.abort())
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def save_manifest(self):
        (self.root / 'assets/cadaver-comparison.json').write_text(json.dumps(self.manifest))

    def open(self):
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}/')
        self.assertTrue(self.page.evaluate('async () => { for(let i=0;i<30;i++){if(window.panel)return true; await new Promise(r=>setTimeout(r,30));} return false;}'), 'mountCadaverPanel export must mount')

    def select(self, part='exact-id', model='fixture-model', system='circulatory'):
        self.page.evaluate('(s)=>window.panel.setSelection(s)', {'modelId': model, 'system': system, 'partId': part})

    def tearDown(self):
        self.page.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def test_exact_selection_displays_original_and_unmapped_is_honest(self):
        self.open()
        self.select()
        image = self.page.locator('#host img')
        expect(image).to_have_count(1)
        self.page.wait_for_function('document.querySelector("#host img")?.naturalWidth === 900')
        self.assertTrue(image.evaluate('(img)=>img.src').endswith('/assets/fixture.svg'))
        expect(self.page.locator('#host')).to_contain_text('Mídia sintética; não valida anatomia.')
        self.select('EXACT-ID')
        expect(image).to_have_count(0)
        expect(self.page.locator('#host')).to_contain_text('Sem correspondência revisada')
        self.assertNotIn('foto inexistente', self.page.locator('#host').inner_text())
        self.assertEqual(self.errors, [])

    def test_modal_focus_mobile_clear_and_model_switch(self):
        self.open()
        self.select()
        button = self.page.get_by_role('button', name='Ampliar original: Original fixture')
        button.click()
        dialog = self.page.get_by_role('dialog')
        expect(dialog).to_be_visible()
        expect(dialog.locator('img')).to_have_attribute('src', self.page.locator('figure img').get_attribute('src'))
        self.page.keyboard.press('Escape')
        expect(dialog).not_to_be_visible()
        expect(button).to_be_focused()
        self.page.set_viewport_size({'width': 360, 'height': 780})
        button.click()
        expect(dialog).to_be_visible()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.page.get_by_role('button', name='Voltar à comparação').click()
        expect(button).to_be_focused()
        button.click()
        self.select(model='other-model')
        expect(dialog).not_to_be_visible()
        expect(self.page.locator('figure img')).to_have_count(0)
        self.select()
        button.click()
        self.page.evaluate('panel.clear()')
        expect(dialog).not_to_be_visible()
        expect(self.page.locator('#host img')).to_have_count(0)
        self.assertEqual(self.errors, [])


    def test_invalid_manifest_and_unsafe_paths_fail_closed(self):
        for bad in ('https://example.org/photo.png', '../private.png', 'assets/../secret.png', 'assets/%2e%2e/secret.png', 'data:image/png;base64,a', '//example.org/a', 'assets/x.png?token=x'):
            with self.subTest(src=bad):
                self.manifest['photos']['original']['src'] = bad
                self.save_manifest()
                self.open()
                self.select()
                expect(self.page.locator('#host')).to_contain_text('manifesto de comparação')
                expect(self.page.locator('#host img')).to_have_count(0)
        self.manifest['photos']['original']['src'] = 'assets/fixture.svg'
        self.manifest['entries'].append(dict(self.manifest['entries'][0]))
        self.save_manifest()
        self.open()
        self.select()
        expect(self.page.locator('#host')).to_contain_text('manifesto de comparação')
        expect(self.page.locator('#host img')).to_have_count(0)
        self.assertEqual(self.errors, [])

    def test_media_failure_and_safe_text(self):
        self.manifest['photos']['original'].update(src='assets/missing.png', title='<img src=x onerror=alert(1)>')
        self.save_manifest()
        self.open()
        self.select()
        expect(self.page.locator('#host')).to_contain_text('Não foi possível abrir esta imagem')
        expect(self.page.locator('figcaption')).to_have_text('<img src=x onerror=alert(1)>')
        expect(self.page.locator('figure img')).not_to_be_visible()
        expect(self.page.get_by_role('button', name='Ampliar original:', exact=False)).to_be_disabled()
        self.assertEqual(self.errors, [])


    def test_pending_load_clear_destroy_and_selection_snapshot(self):
        pending = []
        self.page.route('**/cadaver-comparison.json', lambda route: pending.append(route))
        self.open()
        self.page.wait_for_timeout(80)
        self.select()
        self.page.evaluate('panel.clear()')
        pending.pop().fulfill(json=self.manifest)
        self.page.evaluate('panel.ready')
        expect(self.page.locator('#host img')).to_have_count(0)
        self.page.evaluate('''() => { const selection={modelId:'fixture-model', system:'circulatory', partId:'exact-id'}; panel.setSelection(selection); selection.partId='changed'; }''')
        self.page.evaluate('panel.destroy()')
        expect(self.page.locator('#host')).to_be_empty()
        self.select()
        expect(self.page.locator('#host')).to_be_empty()
        self.assertEqual(self.errors, [])

    def test_http_and_schema_errors_are_honest(self):
        for payload in (None, {'version': 2, 'entries': [], 'photos': {}}, {'version': 1, 'entries': self.manifest['entries'], 'photos': {}}):
            with self.subTest(payload=payload):
                self.page.route('**/cadaver-comparison.json', lambda route, request, value=payload: route.fulfill(status=404, body='missing') if value is None else route.fulfill(json=value))
                self.open()
                self.select()
                expect(self.page.locator('#host')).to_contain_text('manifesto de comparação')
                expect(self.page.locator('#host img')).to_have_count(0)
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
