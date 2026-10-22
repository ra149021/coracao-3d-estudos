"""Local integration: run with atlas-qa-venv, server 8878."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = os.environ.get('ATLAS_QA_URL', 'http://127.0.0.1:8878')
EXPECTED = {
    'coronary_sinus': '006', 'middle_cardiac_vein': '006',
    'posterior_vein_of_left_ventricle': '006', 'left_marginal_vein': '007',
    'anterior_cardiac_vein': '007', 'small_cardiac_vein': '007',
    'left_circumflex_artery': '005', 'right_marginal_artery': '003',
}

class Comparisons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 1000})
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [])

    def open(self):
        self.page.goto(URL + '/coronary-reference.html')
        self.page.wait_for_function('window.coronaryReference?.snapshot().ready', timeout=90000)

    def choose(self, suffix):
        self.page.locator(f'[data-name="VH_F_{suffix}"]').click()

    def test_selection_photo(self):
        self.open()
        self.choose('coronary_sinus')
        photo = self.page.locator('.cadaver-panel figure img')
        self.assertEqual(photo.count(), 1, 'central selection must show reviewed photo')
        photo.evaluate('(img) => img.decode()')
        self.assertTrue(photo.get_attribute('src').endswith('circulatorio_006.png'))

    def test_all_exact_mappings_and_controls(self):
        data = json.loads((ROOT / 'site/assets/coronary-hra/comparisons.json').read_text())
        expected = {'VH_F_' + k: ['circulatorio_' + v] for k, v in EXPECTED.items()}
        self.assertEqual({e['partId']: e['photoIds'] for e in data['entries']}, expected)
        self.assertEqual(len(data['entries']), 8)
        for e in data['entries']:
            self.assertEqual(e['modelId'], 'coronary-reference::hra-blood-vasculature-female-v1.3')
            self.assertEqual(e['runtimeId'], e['partId'])
            self.assertTrue(e['limits'] and e['evidence'] and e['visualLocator'])
        for photo in data['photos'].values():
            self.assertEqual(hashlib.sha256((ROOT / 'site' / photo['src']).read_bytes()).hexdigest(), photo['sha256'])
        self.open()
        baseline = self.page.evaluate('coronaryReference.snapshot().meshes.map(m=>m.matrix)')
        names = self.page.locator('#parts button').evaluate_all('(bs)=>bs.map(b=>b.dataset.name)')
        self.assertEqual(len(names), 17)
        for name in names:
            self.choose(name.removeprefix('VH_F_'))
            self.assertEqual(self.page.evaluate('coronaryReference.snapshot().selected'), name)
            image = self.page.locator('.cadaver-panel figure img')
            if name in expected:
                image.wait_for()
                image.evaluate('(img)=>img.decode()')
                self.assertTrue(image.get_attribute('src').endswith(expected[name][0]+'.png'))
                for field in ['visualLocator', 'evidence', 'limits']:
                    self.assertTrue(self.page.locator('.cadaver-selection-field-'+field).inner_text())
                self.page.locator('#isolate').click()
                self.assertEqual(self.page.evaluate('coronaryReference.snapshot().visibleMeshes'), 1)
                self.assertEqual(image.count(), 1)
                self.page.locator('#isolate').click()
            else:
                self.assertEqual(image.count(), 0)
                self.assertIn('Sem correspondência revisada', self.page.locator('.cadaver-panel').inner_text())
        self.choose('left_anterior_descending_artery')
        self.assertIn('fma8636', self.page.locator('#selection').inner_text())
        self.choose('coronary_sinus')
        self.page.locator('#reset').click()
        self.assertEqual(self.page.locator('.cadaver-panel figure img').count(), 0)
        self.assertIsNone(self.page.evaluate('coronaryReference.snapshot().selected'))
        self.assertEqual(baseline, self.page.evaluate('coronaryReference.snapshot().meshes.map(m=>m.matrix)'))
        self.choose('coronary_sinus')
        self.page.locator('#veins').uncheck()
        self.assertEqual(self.page.locator('.cadaver-panel figure img').count(), 0)
        self.assertIsNone(self.page.evaluate('coronaryReference.snapshot().selected'))

    def test_list_returns_to_visible_comparison(self):
        self.open()
        self.choose('small_cardiac_vein')
        self.page.locator('.cadaver-panel figure img').evaluate('(img)=>img.decode()')
        rect = self.page.locator('.cadaver-panel figure img').bounding_box()
        self.assertGreater(rect['y'] + rect['height'], 0)
        self.assertLess(rect['y'], 1000, 'list selection should bring the photo into view')

    def test_optional_manifest_failures(self):
        for body, status in [('missing', 404), ('{bad json', 200), ('{}', 200)]:
            self.page.route('**/coronary-hra/comparisons.json', lambda route, request, b=body, s=status: route.fulfill(status=s, body=b))
            self.open()
            self.choose('coronary_sinus')
            self.page.get_by_text('Não foi possível carregar o manifesto de comparação.', exact=True).wait_for()
            self.assertTrue(self.page.evaluate('coronaryReference.snapshot().ready'))
            self.page.locator('#isolate').click()
            self.assertEqual(self.page.evaluate('coronaryReference.snapshot().visibleMeshes'), 1)
            self.page.unroute('**/coronary-hra/comparisons.json')

    def test_pending_manifest_and_image_failure(self):
        pending = []
        self.page.route('**/coronary-hra/comparisons.json', lambda route: pending.append(route))
        self.open()
        self.choose('coronary_sinus')
        self.page.get_by_text('Carregando comparações…', exact=True).wait_for()
        self.assertTrue(self.page.evaluate('coronaryReference.snapshot().ready'))
        self.page.locator('#reset').click()
        for route in pending:
            route.continue_()
        self.page.unroute('**/coronary-hra/comparisons.json')
        self.assertEqual(self.page.locator('.cadaver-panel figure img').count(), 0)
        self.page.route('**/circulatorio_006.png', lambda route: route.fulfill(status=404, body='missing'))
        self.choose('coronary_sinus')
        self.page.get_by_text('Não foi possível abrir esta imagem.', exact=False).wait_for()
        self.assertTrue(self.page.get_by_role('button', name='Ampliar original:', exact=False).is_disabled())
        self.assertTrue(self.page.evaluate('coronaryReference.snapshot().ready'))

    def test_raycast_and_modal_reset(self):
        self.open()
        self.page.locator('#wall').select_option('vessels')
        canvas = self.page.locator('#viewport canvas')
        canvas.scroll_into_view_if_needed()
        # Read rendered colors only to target actual mouse clicks, not select API.
        points = canvas.evaluate('''canvas=>{
          const c=document.createElement('canvas');c.width=canvas.width;c.height=canvas.height;
          const ctx=c.getContext('2d');ctx.drawImage(canvas,0,0);
          const {data}=ctx.getImageData(0,0,c.width,c.height);const points=[];
          for(let y=0;y<c.height;y+=7)for(let x=0;x<c.width;x+=7){
            const i=(y*c.width+x)*4,r=data[i],g=data[i+1],b=data[i+2];
            if(r>g*1.4&&r>b*1.3 || b>r*1.3&&b>g*1.15)points.push([x/c.width,y/c.height]);
          }return points;
        }''')
        self.assertTrue(points)
        box = canvas.bounding_box()
        hit = False
        for x, y in points:
            self.page.mouse.click(box['x'] + x*box['width'], box['y'] + y*box['height'])
            if self.page.locator('.cadaver-panel figure img').count():
                hit = True
                break
        self.assertTrue(hit, 'real raycast must reach a reviewed comparison')
        self.page.locator('.cadaver-panel figure img').evaluate('(img)=>img.decode()')
        artifacts = Path(os.environ.get('HRA_QA_ARTIFACTS', '/home/victorzera/.hermes/cache/scratch/hra-comparison-qa'))
        artifacts.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(artifacts / 'desktop-raycast.png'), full_page=True)
        self.page.get_by_role('button', name='Ampliar original:', exact=False).click()
        self.page.locator('#reset').evaluate('(b)=>b.click()')
        self.assertEqual(self.page.locator('dialog[open]').count(), 0)
        self.assertEqual(self.page.locator('.cadaver-panel img').count(), 0)

    def test_modal_zoom_mobile(self):
        self.open()
        for width in [1440, 390]:
            self.page.set_viewport_size({'width': width, 'height': 900})
            self.choose('right_marginal_artery')
            opener = self.page.get_by_role('button', name='Ampliar original:', exact=False)
            opener.click()
            dialog = self.page.locator('dialog[open]')
            self.assertEqual(dialog.count(), 1)
            dialog.locator('img').evaluate('(img)=>img.decode()')
            self.assertIn('segunda foto superior', dialog.inner_text())
            self.page.get_by_role('button', name='Zoom da fotografia').click()
            self.assertEqual(dialog.locator('img').get_attribute('data-zoom'), 'true')
            self.page.keyboard.press('Escape')
            self.assertEqual(self.page.locator('dialog[open]').count(), 0)
            self.assertTrue(opener.evaluate('(el)=>el===document.activeElement'))
            self.assertEqual(self.page.evaluate('coronaryReference.snapshot().selected'), 'VH_F_right_marginal_artery')
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), width)
            opener.click()
            self.page.get_by_role('button', name='Voltar à comparação').click()
            self.assertTrue(opener.evaluate('(el)=>el===document.activeElement'))
        artifacts = Path(os.environ.get('HRA_QA_ARTIFACTS', '/home/victorzera/.hermes/cache/scratch/hra-comparison-qa'))
        artifacts.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(artifacts / 'mobile.png'), full_page=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
