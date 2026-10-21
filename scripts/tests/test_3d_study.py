"""Real Chromium/WebGL regression tests. Run with atlas-qa-venv Python.
Requires the local atlas server on ATLAS_URL (default :8876).
"""
import json
import os
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = os.environ.get('ATLAS_URL', 'http://127.0.0.1:8876')


def assert_viewer_layout_stable(page):
    """Check actual layout, independently of software-WebGL screenshot latency."""
    samples = page.evaluate('''() => new Promise((resolve, reject) => {
      const samples = [];
      const deadline = setTimeout(() => reject(new Error('No layout frames within 90s')), 90000);
      function sample() {
        const r = document.querySelector('#viewer').getBoundingClientRect();
        samples.push([r.x, r.y, r.width, r.height]);
        if (samples.length === 8) { clearTimeout(deadline); resolve(samples); }
        else requestAnimationFrame(sample);
      }
      requestAnimationFrame(sample);
    })''')
    for axis, values in zip(('x', 'y', 'width', 'height'), zip(*samples)):
        if max(values) - min(values) > 0.5:
            raise AssertionError(f'Viewer layout oscillates on {axis}: {samples}')
    return samples[-1]

class Study3D(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else route.abort())

    def tearDown(self):
        self.page.close()

    def load(self, query=''):
        self.page.goto(BASE + '/atlas.html' + query)
        self.page.wait_for_function('window.heartViewer?.snapshot().ready', timeout=90000)
        self.page.wait_for_function('window.heartViewer.snapshot().drawCalls > 0', timeout=60000)

    def snapshot(self):
        return self.page.evaluate('heartViewer.snapshot()')

    def test_isolation_can_restore_exact_previous_context(self):
        self.load()
        self.page.evaluate("heartViewer.show(['heart_00','heart_10','heart_11']); heartViewer.view('posterior'); heartViewer.select('heart_00')")
        before = self.snapshot()
        self.page.locator('#isolate-part').click()
        self.assertEqual(self.snapshot()['visibleParts'], ['heart_00'])
        self.assertEqual(self.page.locator('#restore-context').count(), 1, 'Isolation needs an explicit context restoration control')
        self.page.locator('#restore-context').click()
        after = self.snapshot()
        for key in ['visibleParts', 'selected', 'clipping', 'camera', 'target', 'activeView']:
            self.assertEqual(after[key], before[key], key)
        self.assertFalse(self.errors, self.errors)

    def test_respiratory_context_preserves_neighbours_in_shared_coordinates(self):
        self.load('?system=respiratory')
        self.assertEqual(self.snapshot()['parts'], 190, 'Recovered mediastinal neighbours must supplement, not replace, the original 175 parts')
        self.page.select_option('#study-view', 'mediastino_direito')
        after = self.snapshot()
        self.assertIn('resp_oesophagus', after['visibleParts'])
        self.assertIn('resp_azygos_vein', after['visibleParts'])
        self.assertIn('resp_superior_lobe_of_right_lung', after['visibleParts'])
        self.assertEqual(after['visible'], 10)
        self.assertIn('sulcos permanecem parciais', after['modeNote'])
        self.page.wait_for_timeout(500)
        self.page.screenshot(path=str(ROOT / 'docs/qa/3d/mediastino-direito.png'))
        self.assertFalse(self.errors, self.errors)

    def test_original_and_missing_context_fallback(self):
        for mode in ['disabled', 'fallback']:
            with self.subTest(mode=mode):
                query = '?system=respiratory&context=off' if mode == 'disabled' else '?system=respiratory'
                if mode == 'fallback':
                    self.page.route('**/assets/respiratory-context/model.glb', lambda route: route.fulfill(status=404, body='missing optional model'))
                self.load(query)
                self.assertEqual(self.snapshot()['parts'], 175)
                self.assertEqual(self.snapshot()['contextStatus'], mode)
                self.assertEqual(self.page.locator('#context-note').count(), 1, 'Fallback must be visible to the learner, not only console logs')
                self.assertIn('175', self.page.locator('#context-note').inner_text())
                self.assertGreater(self.snapshot()['triangles'], 0)
                self.assertEqual(self.page.locator('#study-view option[value="mediastino_direito"]').count(), 0)
        self.assertFalse(self.errors, self.errors)

    def test_four_atlases_controls_and_render(self):
        reports = []
        for name, query, count in [('heart', '', 72), ('hra', '?detail=hra', 14),
                                   ('respiratory', '?system=respiratory', 190),
                                   ('larynx', '?system=respiratory&detail=larynx', 40)]:
            with self.subTest(model=name):
                self.load(query)
                initial = self.snapshot()
                self.assertEqual(initial['parts'], count)
                part = initial['visibleParts'][0]
                self.page.evaluate('(id) => heartViewer.select(id)', part)
                self.page.locator('#hide-part').click()
                self.assertNotIn(part, self.snapshot()['visibleParts'])
                self.page.locator('#show-all').click()
                self.assertEqual(self.snapshot()['visible'], count)
                self.page.locator('#reset').click()
                self.assertEqual(self.snapshot()['visibleParts'], initial['visibleParts'])
                self.page.locator('#clipping').check()
                self.assertTrue(self.snapshot()['clipping'])
                self.page.select_option('#cut-axis', 'x')
                self.page.locator('#flip-cut').click()
                self.assertEqual(self.snapshot()['axis'], 'x')
                self.assertTrue(self.snapshot()['flipped'])
                self.page.locator('#reset').click()
                self.assertFalse(self.snapshot()['clipping'])
                for view in ['anterior', 'posterior', 'direita', 'esquerda', 'superior']:
                    self.page.evaluate('(name) => heartViewer.view(name)', view)
                    self.assertEqual(self.snapshot()['activeView'], view)
                self.page.evaluate("heartViewer.view('anterior')")
                self.page.locator('#heart-canvas').focus()
                before = self.snapshot()['camera']
                self.page.keyboard.press('ArrowRight')
                self.page.wait_for_timeout(250)
                self.assertNotEqual(self.snapshot()['camera'], before)
                self.assertIsNone(self.snapshot()['activeView'])
                out = ROOT / 'docs/qa/3d'
                out.mkdir(parents=True, exist_ok=True)
                # SwiftShader can starve animation frames while draining real GL
                # work. Keep Playwright's stability check; budget as for GL loading,
                # and separately reject oscillating layout rather than masking it.
                viewer = self.page.locator('#viewer')
                viewer.scroll_into_view_if_needed(timeout=90000)
                layout = assert_viewer_layout_stable(self.page)
                viewer.screenshot(path=str(out / (name + '-atlas.png')), timeout=90000)
                self.assertEqual(assert_viewer_layout_stable(self.page), layout)
                reports.append({'model': name, **self.snapshot()})
        (ROOT / 'docs/qa/3d/render-snapshots.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
        self.assertFalse(self.errors, self.errors)

    def test_geometry_audit_preserves_sources_and_catalog_identity(self):
        script = ROOT / 'scripts/audit_3d_models.py'
        self.assertTrue(script.is_file(), 'A reproducible GLB validator and recovery inventory must accompany model imports')
        import subprocess
        import sys
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        expected = {'assets/heart.glb': 72, 'assets/heart-hra/model.glb': 14,
                    'assets/larynx/model.glb': 40, 'assets/respiratory/model.glb': 175,
                    'assets/heart-ct/model.glb': 1, 'assets/lung-ct/model.glb': 1,
                    'assets/respiratory-context/model.glb': 15}
        self.assertEqual({v['path']: v['meshes'] for v in report['models']}, expected)
        for model in report['models']:
            self.assertTrue(model['finite'])
            self.assertTrue(model['indices_in_bounds'])
            self.assertTrue(model['catalog_names_match'])
            self.assertGreater(model['triangles'], 0)
        ct = {v['path']: v for v in report['models'] if '-ct/' in v['path']}
        self.assertEqual(ct['assets/heart-ct/model.glb']['sha256'], '326d7ff9755b08714d02bd021eb09715c8314dadc1ef452192e6c9e81d4dae56')
        self.assertEqual(ct['assets/lung-ct/model.glb']['sha256'], 'ccd3875fb64351a8efa4acde7003607013420a8e0c3283ea23e27b7e6ea81a07')
        self.assertEqual(ct['assets/lung-ct/model.glb']['triangles'], 312856)

    def test_selection_offers_only_curated_relationships(self):
        self.load()
        self.page.evaluate("heartViewer.select('heart_00')")
        self.assertEqual(self.page.locator('#selection-relations [data-region="atrio_direito"]').count(), 1,
                         'The atrium must offer its curated caval/valvular relationship, not guessed neighbours')
        self.page.locator('#selection-relations [data-region="atrio_direito"]').click()
        views = json.loads((ROOT / 'site/assets/study-views.json').read_text())
        view = next(v for v in views['circulatory'] if v['id'] == 'atrio_direito')
        after = self.snapshot()
        self.assertEqual(set(after['visibleParts']), set(view['partIds']))
        self.assertEqual(after['transparency'], view['transparency'])
        self.assertIsNone(after['selected'], 'Selection opacity must not override contextual wall translucency')
        self.assertEqual(after['modeNote'], view['note'])
        self.assertIn('não estão individualizados', after['modeNote'])
        self.assertFalse(self.errors, self.errors)

    def test_ct_references_are_local_unsegmented_and_rendered(self):
        for model_id, minimum in [('heart', 1000), ('lung', 312856)]:
            with self.subTest(model=model_id):
                self.page.goto(BASE + '/ct-reference.html?model=' + model_id)
                self.assertEqual(self.page.locator('#ct-status').count(), 1, 'An independent CT reference viewer must be available')
                self.page.wait_for_function('window.ctViewer?.snapshot().drawCalls > 0', timeout=90000)
                snap = self.page.evaluate('ctViewer.snapshot()')
                self.assertGreaterEqual(snap['triangles'], minimum)
                self.assertEqual(snap['segmentedParts'], 0)
                self.assertIn('sem segmentação', self.page.locator('#ct-limits').inner_text())
                before = snap['camera']
                self.page.locator('#ct-zoom-in').click()
                self.page.wait_for_timeout(150)
                self.assertNotEqual(self.page.evaluate('ctViewer.snapshot().camera'), before)
                self.page.locator('#ct-fit').click()
                self.page.wait_for_timeout(150)
                self.assertEqual(self.page.evaluate('ctViewer.snapshot().camera'), before)
                out = ROOT / 'docs/qa/3d'
                out.mkdir(parents=True, exist_ok=True)
                self.page.screenshot(path=str(out / ('ct-' + model_id + '.png')))
        self.assertFalse(self.errors, self.errors)

if __name__ == '__main__':
    unittest.main()
