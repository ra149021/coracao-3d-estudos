"""Static release: real catalog/mesh selections; no private staging dependency."""
import copy
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

FREEZE = Path(__file__).with_name('fixtures') / 'cadaver-coverage.json'


def selection_key(entry):
    return tuple(entry[field] for field in ('modelId', 'system', 'partId'))


def coverage_contract(test, actual, expected):
    """Compare observed identities to reviewed disk fixture, never regenerate it."""
    wanted = expected['expectedSelections']
    test.assertEqual(len(actual['entries']), len(wanted), 'selection count')
    for entries in (actual['entries'], wanted):
        test.assertEqual(len({selection_key(e) for e in entries}), len(entries), 'duplicate selection')
    test.assertEqual({selection_key(e): e['photoIds'] for e in actual['entries']},
                     {selection_key(e): e['photoIds'] for e in wanted}, 'selection/photo identity')
    test.assertEqual({key: {field: photo[field] for field in ('src', 'sha256')}
                      for key, photo in actual['photos'].items()}, expected['photos'], 'photo identity')


def catalog_labels(model, read_json, context=True):
    parts = list(read_json(CATALOGS[model])['parts'])
    if model == 'respiratory' and context:
        parts.extend(read_json('assets/respiratory-context/parts.json')['parts'])
    labels = {p['id']: p['label'] for p in parts}
    if len(labels) != len(parts):
        raise AssertionError('duplicate catalog identity')
    return labels


class CadaverCoverageContract(unittest.TestCase):
    """Lightweight negative controls; no WebGL, no active-manifest expectations."""
    def setUp(self):
        self.expected = json.loads(FREEZE.read_text())
        self.actual = {'entries': copy.deepcopy(self.expected['expectedSelections']),
                       'photos': copy.deepcopy(self.expected['photos'])}

    def test_context_catalog_is_included_only_when_enabled(self):
        read = lambda path: json.loads((ROOT / 'site' / path).read_text())
        enabled = catalog_labels('respiratory', read)
        disabled = catalog_labels('respiratory', read, context=False)
        self.assertIn('resp_ascending_aorta', enabled)
        self.assertNotIn('resp_ascending_aorta', disabled)
        context = read('assets/respiratory-context/parts.json')['parts']
        self.assertEqual(set(enabled) - set(disabled), {p['id'] for p in context})
        for entry in self.expected['expectedSelections']:
            self.assertIn(entry['partId'], catalog_labels(entry['modelId'], read))

    def test_local_release_matches_reviewed_freeze_and_photo_bytes(self):
        actual = json.loads((ROOT / 'site/assets/cadaver-comparison.json').read_text())
        coverage_contract(self, actual, self.expected)
        for photo in self.expected['photos'].values():
            self.assertEqual(hashlib.sha256((ROOT / 'site' / photo['src']).read_bytes()).hexdigest(), photo['sha256'])

    def test_baseline_contract(self):
        coverage_contract(self, self.actual, self.expected)

    def test_same_count_substitutions_and_duplicates_are_rejected(self):
        for field, value in [('partId', 'unapproved-part'), ('system', 'wrong-system'),
                             ('modelId', 'wrong-model'), ('photoIds', ['unapproved-photo']),
                             ('photoIds', [next(p for p in self.actual['photos']
                                                if p not in self.actual['entries'][0]['photoIds'])])]:
            with self.subTest(field=field):
                altered = copy.deepcopy(self.actual)
                altered['entries'][0][field] = value
                with self.assertRaises(AssertionError):
                    coverage_contract(self, altered, self.expected)
        altered = copy.deepcopy(self.actual)
        altered['entries'][0] = copy.deepcopy(altered['entries'][1])
        with self.assertRaises(AssertionError):
            coverage_contract(self, altered, self.expected)

    def test_removal_and_unapproved_addition_are_rejected(self):
        for entries in [self.actual['entries'][1:], self.actual['entries'] + [self.actual['entries'][0]]]:
            with self.assertRaises(AssertionError):
                coverage_contract(self, {**self.actual, 'entries': entries}, self.expected)

    def test_photo_path_and_hash_substitution_are_rejected(self):
        for field, value in [('src', 'assets/substitute.png'), ('sha256', '0' * 64)]:
            with self.subTest(field=field):
                altered = copy.deepcopy(self.actual)
                altered['photos'][next(iter(altered['photos']))][field] = value
                with self.assertRaises(AssertionError):
                    coverage_contract(self, altered, self.expected)


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
        self.assertFalse(self.errors, self.errors)

    def test_all_explicit_selections_decode_originals_and_clear(self):
        expected = json.loads(FREEZE.read_text())
        # Observe the served release, including remote ATLAS_URL; expectations stay local/frozen.
        def served_json(path):
            response = self.page.request.get(BASE.rstrip('/') + '/' + path)
            self.assertTrue(response.ok, f'HTTP {response.status}: {path}')
            return response.json()
        manifest = served_json('assets/cadaver-comparison.json')
        coverage_contract(self, manifest, expected)
        for forbidden in ['/home/', 'noteId', 'docs/qa', 'sourceAbsolutePath']:
            self.assertNotIn(forbidden, json.dumps(manifest))
        for blocked in ['respiratorio_022', 'respiratorio_023', 'respiratorio_005', 'respiratorio_006']:
            self.assertNotIn(blocked, manifest['photos'])
        for key, photo in expected['photos'].items():
            response = self.page.request.get(BASE.rstrip('/') + '/' + photo['src'])
            self.assertTrue(response.ok, f'photo HTTP {response.status}: {key}')
            self.assertEqual(hashlib.sha256(response.body()).hexdigest(), photo['sha256'], key)
        reports = []
        out = OUT
        out.mkdir(parents=True, exist_ok=True)
        for model in QUERIES:
            self.load(model)
            self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
            entries = [e for e in expected['expectedSelections'] if e['modelId'] == model]
            labels = catalog_labels(model, served_json)
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
                    actual_entry = next(e for e in manifest['entries'] if selection_key(e) == selection_key(entry))
                    qualifications = []
                    for field in ('evidence', 'visualLocator', 'limits', 'status'):
                        value = actual_entry.get(field, [])
                        qualifications.extend(value if isinstance(value, list) else [value])
                    for value in qualifications:
                        if isinstance(value, str) and value.strip():
                            self.assertIn(value, self.page.locator('#cadaver-host').inner_text())
                    self.page.locator('#cadaver-host figure button').first.click()
                    for value in qualifications:
                        if isinstance(value, str) and value.strip():
                            self.assertIn(value, self.page.locator('.cadaver-panel-dialog').inner_text())
                    self.page.wait_for_function('document.querySelector(".cadaver-panel-dialog[open] img")?.naturalWidth > 0')
                    self.page.keyboard.press('Escape')
                    self.assertEqual(self.page.locator('.cadaver-panel-dialog[open]').count(), 0)
                    self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), entry['partId'])
                    self.page.locator('#reset').click()
                    self.assertEqual(self.page.locator('#cadaver-host img').count(), 0)
                    reports.append({'modelId':model,'system':entry['system'],'partId':entry['partId'],'photoIds':entry['photoIds'],'images':images,'zoomReturnReset':'PASS'})
                    (out / 'runtime-selections.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
            # API/reset/quiz integration must use the same selection hook.
            if not entries:
                self.assertFalse(self.errors, self.errors)
                continue
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
            missing = next((i for i in self.page.evaluate('heartViewer.snapshot().visibleParts') if i not in mapped), None)
            if missing is not None:
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
        self.assertEqual(len(reports), len(expected['expectedSelections']))
        self.assertEqual(len({selection_key(e) for e in reports}), len(reports))
        self.assertEqual({selection_key(e) for e in reports}, {selection_key(e) for e in expected['expectedSelections']})
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
        buttons = self.page.locator('#cadaver-host figure button')
        self.assertGreater(buttons.count(), 0)
        for index in range(buttons.count()):
            buttons.nth(index).click()
            self.page.wait_for_function('document.querySelector(".cadaver-panel-dialog[open] img")?.naturalWidth > 0')
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 390)
            self.page.keyboard.press('Escape')
            self.assertEqual(self.page.evaluate('heartViewer.snapshot().selected'), 'larynx_fma55130')
        out = OUT
        out.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(out / 'mobile.png'))
        self.assertFalse(self.errors, self.errors)

if __name__ == '__main__':
    unittest.main()
