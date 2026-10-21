"""Static release: real catalog/mesh selections; no private staging dependency."""
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('ATLAS_URL', 'http://127.0.0.1:8878')
OUT = Path(os.environ.get('ATLAS_QA_OUTPUT', str(Path(tempfile.gettempdir()) / 'atlas-cadaver-integration')))
CATALOGS = {'heart': 'assets/catalog.json', 'hra': 'assets/heart-hra/catalog.json',
            'respiratory': 'assets/respiratory/catalog.json', 'larynx': 'assets/larynx/catalog.json'}
QUERIES = {'heart': '', 'hra': '?detail=hra', 'respiratory': '?system=respiratory',
           'larynx': '?system=respiratory&detail=larynx'}

class CadaverIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width':1440, 'height':1000}, reduced_motion='reduce')
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(BASE) else r.abort())
        self.page.set_default_timeout(90000)

    def tearDown(self):
        self.page.close()

    def load(self, model):
        self.page.goto(BASE + '/atlas.html' + QUERIES[model])
        self.page.wait_for_function('window.heartViewer?.snapshot().ready && heartViewer.snapshot().drawCalls > 0')

    def test_panel_is_mounted_in_real_atlas(self):
        self.load('hra')
        self.assertEqual(self.page.locator('#cadaver-host .cadaver-panel').count(), 1)

    def test_all_explicit_selections_decode_originals_and_clear(self):
        manifest = json.loads((ROOT / 'site/assets/cadaver-comparison.json').read_text())
        # Published hashes preserve byte identity without shipping private Anki staging.
        self.assertEqual(len(manifest['entries']), 43)
        self.assertEqual(len(manifest['photos']), 16)
        self.assertEqual(len({(e['modelId'], e['system'], e['partId']) for e in manifest['entries']}), 43)
        for forbidden in ['/home/', 'noteId', 'docs/qa', 'sourceAbsolutePath']:
            self.assertNotIn(forbidden, json.dumps(manifest))
        for blocked in ['respiratorio_022', 'respiratorio_023', 'respiratorio_005', 'respiratorio_006']:
            self.assertNotIn(blocked, manifest['photos'])
        for key, photo in manifest['photos'].items():
            self.assertEqual(hashlib.sha256((ROOT / 'site' / photo['src']).read_bytes()).hexdigest(), photo['sha256'])
        reports = []
        out = OUT
        out.mkdir(parents=True, exist_ok=True)
        for model in QUERIES:
            self.load(model)
            self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
            entries = [e for e in manifest['entries'] if e['modelId'] == model]
            self.assertEqual(len(entries), {'heart':18, 'hra':5, 'respiratory':11, 'larynx':9}[model])
            catalog = json.loads((ROOT / 'site' / CATALOGS[model]).read_text())
            labels = {p['id']: p['label'] for p in catalog['parts']}
            for entry in entries:
                with self.subTest(model=model, part=entry['partId']):
                    before = self.page.evaluate('heartViewer.snapshot().visibleParts')
                    # Actual catalog list button, not a synthetic panel event.
                    self.page.locator('#search').fill(labels[entry['partId']])
                    row = self.page.locator(f'[data-id="{entry["partId"]}"] .part-select')
                    self.assertEqual(row.count(), 1)
                    row.click()
                    self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), entry['partId'])
                    self.assertTrue(set(before).issubset(self.page.evaluate('heartViewer.snapshot().visibleParts')))
                    self.page.wait_for_function('''() => {
                      const images = [...document.querySelectorAll('#cadaver-host figure img')];
                      return images.length && images.every(i => i.complete && i.naturalWidth > 0);
                    }''')
                    images = self.page.locator('#cadaver-host figure img').evaluate_all('(imgs) => imgs.map(i => ({src:i.getAttribute("src"),width:i.naturalWidth,height:i.naturalHeight}))')
                    self.assertEqual(len(images), len(entry['photoIds']))
                    for image, photo_id in zip(images, entry['photoIds']):
                        self.assertTrue(image['src'].endswith(manifest['photos'][photo_id]['src']))
                    for photo_id in entry['photoIds']:
                        self.assertIn(manifest['photos'][photo_id]['evidence'], self.page.locator('#cadaver-host').text_content())
                    self.page.locator('#cadaver-host figure button').first.click()
                    self.page.wait_for_function('document.querySelector(".cadaver-panel-dialog[open] img")?.naturalWidth > 0')
                    self.page.keyboard.press('Escape')
                    self.assertEqual(self.page.locator('.cadaver-panel-dialog[open]').count(), 0)
                    self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), entry['partId'])
                    self.page.locator('#reset').click()
                    self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
                    reports.append({'model':model,'partId':entry['partId'],'images':images,'zoomReturnReset':'PASS'})
                    (out / 'runtime-selections.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
            # API/reset/quiz integration must use the same selection hook.
            target = entries[0]['partId']
            self.page.evaluate('(id) => heartViewer.select(id)', target)
            self.page.locator('#cadaver-host figure button').first.click()
            self.page.keyboard.press('Escape')
            self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), target)
            self.assertEqual(self.page.locator('.cadaver-panel-dialog[open]').count(), 0)
            self.page.evaluate('heartViewer.setExamMode(true)')
            self.page.evaluate('(id) => heartViewer.select(id)', target)
            self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
            self.page.evaluate('heartViewer.setExamMode(false)')
            self.page.locator('#reset').click()
            self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
            mapped = {e['partId'] for e in entries}
            missing = next(i for i in self.page.evaluate('heartViewer.snapshot().visibleParts') if i not in mapped)
            self.page.evaluate('(id) => heartViewer.select(id)', missing)
            self.assertIn('Isso não indica ausência de foto', self.page.locator('#cadaver-host').inner_text())
            self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
            self.page.evaluate('(id) => heartViewer.select(id)', target)
            self.page.wait_for_function('document.querySelector("#cadaver-host figure img")?.naturalWidth > 0')
            out = OUT
            out.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(out / (model + '.png')))
            # Switch through the real model navigation with a photo still selected.
            next_model = {'heart':'hra', 'hra':'heart', 'respiratory':'larynx', 'larynx':'respiratory'}[model]
            href = 'atlas.html' + QUERIES[next_model]
            self.page.locator(f'a.reference-link[href="{href}"]').first.click()
            self.page.wait_for_function('window.heartViewer?.snapshot().ready && heartViewer.snapshot().drawCalls > 0')
            self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
            self.assertFalse(self.page.evaluate('heartViewer.snapshot().selected'))
        self.assertEqual(len(reports), 43)
        (out / 'runtime-selections.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
        self.assertFalse(self.errors, self.errors)

    def test_ray_cast_selection_uses_same_comparison_hook(self):
        self.load('heart')
        # Explicit isolation is only a test setup to give the ray a known target.
        self.page.evaluate("heartViewer.show(['heart_04']); heartViewer.view('anterior'); heartViewer.clear()")
        canvas = self.page.locator('#heart-canvas')
        canvas.scroll_into_view_if_needed()
        box = canvas.bounding_box()
        for x, y in [(0.5, 0.5), (0.4, 0.5), (0.6, 0.5), (0.5, 0.4), (0.5, 0.6)]:
            canvas.click(position={'x':box['width'] * x,'y':box['height'] * y})
            if self.page.evaluate('heartViewer.snapshot().selected') == 'heart_04':
                break
        self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), 'heart_04')
        self.page.wait_for_function('document.querySelector("#cadaver-host figure img")?.naturalWidth > 0')
        self.assertIn('Aorta ascendente', self.page.locator('#cadaver-host').inner_text())
        self.page.locator('#hide-part').click()
        self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
        self.assertFalse(self.errors, self.errors)

    def test_mobile_comparison_has_no_horizontal_overflow(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.load('larynx')
        self.page.evaluate("heartViewer.select('larynx_fma55130')")
        self.page.wait_for_function('document.querySelector("#cadaver-host figure img")?.naturalWidth > 0')
        self.assertIn('tireoepiglótico à esquerda', self.page.locator('#cadaver-host').inner_text())
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 390)
        self.page.locator('#cadaver-host figure button').click()
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 390)
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), 'larynx_fma55130')
        out = OUT
        out.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(out / 'mobile.png'))
        self.assertFalse(self.errors, self.errors)

if __name__ == '__main__':
    unittest.main()
