"""Independent utility QA, not anatomy certification. Needs local server :8876.
Run with /home/victorzera/Estudos/atlas-qa-venv/bin/python -m unittest scripts.tests.test_3d_usability -v
Evidence goes to ATLAS_QA_OUT or $TMPDIR/atlas-usability-fixes; historical audit evidence is preserved.
Defect assertions are NOT expectedFailure.
"""
import json
import os
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('ATLAS_QA_OUT', str(Path(os.environ.get('TMPDIR', str(ROOT))) / 'atlas-usability-fixes')))
BASE = os.environ.get('ATLAS_URL', 'http://127.0.0.1:8876')
MODELS = [('heart', '', 'catalog.json', 72), ('hra', '?detail=hra', 'heart-hra/catalog.json', 14),
          ('larynx', '?system=respiratory&detail=larynx', 'larynx/catalog.json', 40),
          ('respiratory', '?system=respiratory', 'respiratory/catalog.json', 190)]
KEYS = ['visibleParts', 'selected', 'preset', 'camera', 'target', 'clipping', 'axis', 'cut',
        'flipped', 'transparency', 'labels', 'palette', 'activeView', 'viewName', 'modeNote']

class Utility3D(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUT.mkdir(parents=True, exist_ok=True)
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def page(self, width=1440):
        p = self.browser.new_page(viewport={'width': width, 'height': 1000 if width > 390 else 844}, reduced_motion='reduce')
        p.set_default_timeout(12000)
        p.set_default_navigation_timeout(90000)  # Local large GLB transfers may outlast UI waits.
        p.route('**/*', lambda r: r.continue_() if r.request.url.startswith(BASE) else r.abort())
        return p

    def load(self, p, query=''):
        p.goto(BASE + '/atlas.html' + query)
        p.wait_for_function('window.heartStudy && heartViewer.snapshot().drawCalls > 0', timeout=90000)

    def snap(self, p):
        return p.evaluate('heartViewer.snapshot()')

    def capture(self, p, name, viewer=False):
        p.wait_for_timeout(160)
        target = p.locator('#viewer') if viewer else p
        target.screenshot(path=str(OUT / (name + '.png')), **({} if viewer else {'full_page': True}))

    def save(self, name, data):
        (OUT / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    def range(self, p, selector, value):
        p.locator(selector).focus()
        p.locator(selector).press('Home')
        for _ in range(value // 10):
            p.locator(selector).press('PageUp')
        for _ in range(value % 10):
            p.locator(selector).press('ArrowRight')

    def assert_label_layout(self, p):
        labels = p.locator('.mesh-label:visible').evaluate_all('es=>es.map(e=>({id:e.dataset.partId,rect:e.getBoundingClientRect().toJSON()}))')
        for i, a in enumerate(labels):
            for b in labels[i+1:]:
                ra, rb = a['rect'], b['rect']
                self.assertFalse(min(ra['right'],rb['right'])-max(ra['left'],rb['left'])>1 and min(ra['bottom'],rb['bottom'])-max(ra['top'],rb['top'])>1, f'Label collision: {a["id"]}/{b["id"]}')
        return labels

    def test_01_desktop_and_mobile_real_study_sessions(self):
        reports, defects = [], []
        for width in [1440, 390]:
            for name, query, catalog_path, count in MODELS:
                with self.subTest(width=width, model=name):
                    p = self.page(width)
                    errors = []
                    p.on('pageerror', lambda e: errors.append(str(e)))
                    r = {'model': name, 'width': width}
                    try:
                        self.load(p, query)
                        self.assertEqual(self.snap(p)['parts'], count)
                        catalog = json.loads((ROOT / 'site/assets' / catalog_path).read_text())
                        options = p.locator('#study-view option').evaluate_all('(es)=>es.map(e=>({id:e.value,label:e.textContent}))') if p.locator('#study-view').count() else []
                        if len(options)>1:
                            region = options[3 if len(options)>3 else 1]
                            p.select_option('#study-view', region['id'])
                            r['region'] = region
                        else:
                            presets = p.locator('[data-preset]').evaluate_all('(es)=>es.map(e=>({id:e.dataset.preset,label:e.textContent}))')
                            r['region'] = presets[1]
                            p.locator('[data-preset]').nth(1).click()
                        p.locator('[data-view="posterior"]').click()
                        state = self.snap(p)
                        part = next(x for x in catalog['parts'] if x['id'] in state['visibleParts'] and x.get('quizEligible') is not False)
                        p.locator('#search').fill(part['label'])
                        p.locator(f'[data-id="{part["id"]}"] .part-select').click()
                        self.assertEqual(self.snap(p)['selected'], part['id'])
                        r['target'] = part['label']
                        p.locator('#labels').click()
                        self.range(p, '#transparency', 65)
                        p.locator('#clipping').check()
                        p.select_option('#cut-axis', 'x')
                        self.range(p, '#cut-position', 42)
                        p.locator('#flip-cut').click()
                        before = self.snap(p)
                        self.capture(p, f'{name}-{width}-before-isolate')
                        p.locator('#isolate-part').click()
                        self.assertEqual(self.snap(p)['visibleParts'], [part['id']])
                        self.capture(p, f'{name}-{width}-isolated', True)
                        p.locator('#restore-context').click()
                        after = self.snap(p)
                        r['restorationDifferences'] = {k: [before[k], after[k]] for k in KEYS if before[k] != after[k]}
                        if r['restorationDifferences']:
                            defects.append(f'{name}/{width}: context restoration {list(r["restorationDifferences"])}')
                        p.locator('#hide-part').click()
                        self.assertNotIn(part['id'], self.snap(p)['visibleParts'])
                        p.locator(f'[data-id="{part["id"]}"] .visibility').click()
                        self.assertIn(part['id'], self.snap(p)['visibleParts'])
                        if p.locator('#clear-selection').is_visible():
                            p.locator('#clear-selection').click()
                        p.locator('#clipping').uncheck()
                        self.range(p, '#transparency', 65)
                        self.capture(p, f'{name}-{width}-context', True)
                        r['labels'] = p.locator('.mesh-label:visible').evaluate_all('es=>es.map(e=>({text:e.textContent,rect:e.getBoundingClientRect().toJSON(),font:getComputedStyle(e).fontSize}))')
                        r['layout'] = p.evaluate('''()=>{let ids=['viewer','isolate-part','transparency','study-view'];return {viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,scrollY,boxes:Object.fromEntries(ids.map(id=>[id,document.getElementById(id)?.getBoundingClientRect().toJSON()]))}}''')
                        exploration = self.snap(p)
                        p.locator('.study-launch').click()
                        p.select_option('#study-mode', 'identify')
                        p.locator('#study-setup button[type="submit"]').click()
                        p.wait_for_timeout(160)
                        r['quiz'] = p.evaluate('({study:heartStudy.snapshot(),view:heartViewer.snapshot(),storage:Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith("atlas:practice:v3")))})')
                        self.capture(p, f'{name}-{width}-identify')
                        p.get_by_role('button', name='Revelar resposta', exact=True).click()
                        r['revealedAnswer'] = p.locator('.study-feedback').inner_text()
                        p.get_by_role('button', name='Pausar e explorar', exact=True).click()
                        paused = self.snap(p)
                        r['practiceRestorationDifferences'] = {k: [exploration[k], paused[k]] for k in KEYS if exploration[k] != paused[k]}
                        if r['practiceRestorationDifferences']:
                            defects.append(f'{name}/{width}: practice restoration {list(r["practiceRestorationDifferences"])}')
                        p.locator('.study-launch').click()
                        p.select_option('#study-mode', 'find')
                        p.locator('#study-setup button[type="submit"]').click()
                        r['findQuestion'] = p.locator('#study-question').inner_text()
                        self.capture(p, f'{name}-{width}-find')
                        p.get_by_role('button', name='Pausar e explorar', exact=True).click()
                        # Follow the actual reading link, without modifying theory.
                        reading = p.locator('a[href*="theory.html"]').first
                        r['readingLink'] = reading.get_attribute('href')
                        if not reading.is_visible():
                            p.get_by_role('button', name='Menu', exact=True).click()
                        reading.click()
                        p.wait_for_load_state('domcontentloaded')
                        r['readingURL'] = p.url
                        r['readingHeading'] = p.locator('h1').first.inner_text()
                        self.assertIn('theory.html', p.url)
                        r['errors'] = errors
                        self.assertFalse(errors)
                    finally:
                        reports.append(r)
                        self.save('sessions', reports)
                        p.close()
        self.assertEqual(defects, [], '\n'.join(defects))

    def test_02_every_named_view_and_context_target_is_visible(self):
        reports = []
        views = json.loads((ROOT / 'site/assets/study-views.json').read_text())
        extra = json.loads((ROOT / 'site/assets/respiratory-context/parts.json').read_text())
        for width in [1440,390]:
            for name, query, catpath, _ in MODELS:
                p = self.page(width)
                try:
                    self.load(p, query)
                    catalog = json.loads((ROOT/'site/assets'/catpath).read_text())
                    region_views = list(views['circulatory' if name=='heart' else 'respiratory']) if name in ['heart','respiratory'] else catalog.get('presets', [])
                    if name=='respiratory':
                        catalog['parts'] += extra['parts']
                        region_views += extra['views']
                    for v in region_views:
                        if p.locator(f'#study-view option[value="{v["id"]}"]').count():
                            p.select_option('#study-view', v['id'])
                        elif p.locator(f'[data-preset="{v["id"]}"]').count():
                            p.locator(f'[data-preset="{v["id"]}"]').click()
                        else:
                            continue
                        p.locator('#labels').click() if self.snap(p)['labels'] is False else None
                        s = self.snap(p)
                        expected = v.get('partIds')
                        if expected:
                            self.assertEqual(set(s['visibleParts']), set(expected))
                        # Project catalog bounding corners with the real camera, no screenshot-based anatomy inference.
                        projection = p.evaluate('''async parts=>{const T=await import('./vendor/three/build/three.module.js');let s=heartViewer.snapshot(),c=document.querySelector('#heart-canvas'),cam=new T.PerspectiveCamera(34,c.clientWidth/c.clientHeight,.01,150);cam.position.fromArray(s.camera);cam.lookAt(new T.Vector3(...s.target));cam.updateMatrixWorld();return parts.filter(p=>s.visibleParts.includes(p.id)).map(p=>{let points=[];for(let x of [p.bounds[0][0],p.bounds[1][0]])for(let y of [p.bounds[0][1],p.bounds[1][1]])for(let z of [p.bounds[0][2],p.bounds[1][2]])points.push(new T.Vector3(x,y,z).project(cam).toArray());return {id:p.id,label:p.label,outside:points.some(p=>Math.abs(p[0])>1||Math.abs(p[1])>1||p[2]<-1||p[2]>1),extent:[Math.min(...points.map(p=>p[0])),Math.max(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),Math.max(...points.map(p=>p[1]))]}})}''', catalog['parts'])
                        self.capture(p, f'view-{name}-{width}-{v["id"]}', True)
                        self.assert_label_layout(p)
                        self.assertTrue(p.locator('#label-status').is_visible())
                        reports.append({'model':name,'width':width,'id':v['id'],'focusPartIds':v.get('focusPartIds',s['visibleParts']),'snapshot':s,'projection':projection,'labels':p.locator('.mesh-label:visible').all_text_contents()})
                        self.save('named-views',reports)
                finally:
                    p.close()
        self.assertTrue(reports)
        # Clipped context may be intentional when focusPartIds explicitly narrows the framing.
        clipped = [(r['model'],r['width'],r['id'],p['id']) for r in reports for p in r['projection'] if p['outside']]
        self.save('projected-outside',clipped)
        focus_clipped = [(r['model'],r['width'],r['id'],p['id']) for r in reports for p in r['projection'] if p['outside'] and p['id'] in r['focusPartIds']]
        self.assertEqual(focus_clipped, [], 'Curated focal target bounds exceed camera frame: '+str(focus_clipped))

    def test_03_ct_controls_and_failure_return_paths(self):
        reports=[]
        for width in [1440,390]:
            for model in ['heart','lung']:
                p=self.page(width)
                p.set_default_timeout(60000)  # CT software rendering can block input for several frames.
                try:
                    p.goto(BASE+'/ct-reference.html?model='+model)
                    p.wait_for_function('window.ctViewer?.snapshot().drawCalls>0',timeout=90000)
                    initial=p.evaluate('ctViewer.snapshot()')
                    host=p.locator('#ct-host').bounding_box()
                    p.mouse.move(host['x']+host['width']*.5,host['y']+host['height']*.5)
                    p.mouse.down();p.mouse.move(host['x']+host['width']*.65,host['y']+host['height']*.55,steps=6);p.mouse.up()
                    p.wait_for_timeout(300)
                    rotated=p.evaluate('ctViewer.snapshot()')
                    self.assertNotEqual(initial['camera'],rotated['camera'])
                    p.locator('#ct-zoom-in').click();p.locator('#ct-zoom-out').click();p.locator('#ct-fit').click()
                    fitted=p.evaluate('ctViewer.snapshot()')
                    # Fit restores scale/centering; residual OrbitControls damping may change angle.
                    import math
                    self.assertAlmostEqual(math.dist(initial['camera'],initial['target']), math.dist(fitted['camera'],fitted['target']), places=6)
                    self.assertEqual(initial['target'],fitted['target'])
                    self.assertEqual(fitted['segmentedParts'],0)
                    self.capture(p,f'ct-{model}-{width}')
                    r={'model':model,'width':width,'initial':initial,'rotated':rotated,'fitted':fitted,'limits':p.locator('#ct-limits').inner_text(),'back':p.locator('#ct-back').get_attribute('href')}
                    p.locator('#ct-back').click(no_wait_after=True)
                    p.wait_for_url('**/atlas.html*', wait_until='domcontentloaded', timeout=90000)
                    p.wait_for_function('window.heartStudy && heartViewer.snapshot().drawCalls>0', timeout=90000)
                    reports.append(r);self.save('ct',reports)
                finally:p.close()
        for model in ['heart','lung']:
            p=self.page(390)
            try:
                p.route('**/assets/'+model+'-ct/model.glb',lambda r:r.fulfill(status=404,body='QA missing CT'))
                p.goto(BASE+'/ct-reference.html?model='+model)
                p.wait_for_function('document.querySelector("#ct-status").textContent.includes("Não")',timeout=90000)
                self.capture(p,'ct-'+model+'-404')
                self.assertTrue(p.locator('#ct-back').is_visible())
                reports.append({'model':model,'failure':p.locator('#ct-status').inner_text(),'back':p.locator('#ct-back').get_attribute('href')})
                self.save('ct',reports)
            finally:p.close()

    def test_04_respiratory_fallback_is_explicit_and_still_useful(self):
        reports=[]
        for width in [1440,390]:
            for failure in ['off','404']:
                p=self.page(width)
                try:
                    if failure=='404':p.route('**/assets/respiratory-context/model.glb',lambda r:r.fulfill(status=404,body='QA missing supplement'))
                    self.load(p,'?system=respiratory'+('&context=off' if failure=='off' else ''))
                    self.assertEqual(self.snap(p)['parts'],175)
                    self.assertIn('175',p.locator('#context-note').inner_text())
                    p.select_option('#study-view','arvore_superior_direito')
                    p.locator('#search').fill('Traqueia')
                    p.locator('[data-id="resp_trachea"] .part-select').click()
                    before=self.snap(p)
                    p.locator('#isolate-part').click();p.locator('#restore-context').click()
                    self.assertEqual(self.snap(p)['visibleParts'],before['visibleParts'])
                    self.capture(p,f'fallback-{failure}-{width}')
                    reports.append({'width':width,'failure':failure,'note':p.locator('#context-note').inner_text(),'snapshot':self.snap(p)})
                    self.save('fallback',reports)
                finally:p.close()

    def test_05_no_explicit_aggregates_in_identification_queue(self):
        catalog = json.loads((ROOT/'site/assets/respiratory/catalog.json').read_text())
        aggregates = [x for x in catalog['parts'] if x.get('representation')=='aggregate' and x.get('quizEligible') is not False]
        p = self.page(390)
        try:
            self.load(p, '?system=respiratory')
            p.locator('.study-launch').click()
            p.select_option('#study-group','seios')
            p.select_option('#study-mode','find')
            p.locator('#study-setup button[type="submit"]').click()
            queue = p.evaluate('JSON.parse(localStorage.getItem("atlas:practice:v3:respiratory")).session.queue')
            excluded = {x['id'] for x in aggregates}
            self.save('aggregate-quiz', {'queue': queue, 'forbidden': sorted(excluded)})
            self.assertFalse(excluded.intersection(queue), 'Explicit aggregate representations remain in the real find queue: '+str(sorted(excluded.intersection(queue))))
        finally:
            p.close()

    def test_06_mobile_labels_do_not_overlap(self):
        p=self.page(390)
        try:
            self.load(p,'?system=respiratory&detail=larynx')
            p.locator('[data-preset="profunda"]').click()
            p.locator('[data-view="posterior"]').click()
            p.locator('#labels').click()
            p.wait_for_timeout(200)
            labels=p.locator('.mesh-label:visible').evaluate_all('es=>es.map(e=>({text:e.textContent,rect:e.getBoundingClientRect().toJSON()}))')
            overlaps=[]
            for i,a in enumerate(labels):
                for b in labels[i+1:]:
                    ra,rb=a['rect'],b['rect']
                    w=min(ra['right'],rb['right'])-max(ra['left'],rb['left'])
                    h=min(ra['bottom'],rb['bottom'])-max(ra['top'],rb['top'])
                    if w>1 and h>1:overlaps.append({'a':a['text'],'b':b['text'],'area':w*h})
            self.capture(p,'labels-larynx-mobile',True)
            self.save('label-overlaps',{'labels':labels,'overlaps':overlaps})
            self.assertEqual(overlaps,[], 'Visible anatomical labels collide and hide names: '+str(overlaps))
        finally:p.close()

    def test_07_mobile_result_access_preserves_every_view_setting(self):
        p = self.page(390)
        try:
            self.load(p)
            p.locator('#search').fill('Átrio direito')
            p.locator('.part-select').first.click()
            p.locator('#isolate-part').click()
            p.wait_for_timeout(650)  # Wait for deliberate camera animation before testing scroll-only state.
            before = self.snap(p)
            self.assertEqual(p.get_by_role('button', name='Ver resultado na cena', exact=True).count(), 1, 'No explicit scene-result access from distant controls')
            p.get_by_role('button', name='Ver resultado na cena', exact=True).click()
            box = p.locator('#viewer').bounding_box()
            self.assertGreaterEqual(box['y'], -1)  # CSS subpixel scroll rounding.
            self.assertLess(box['y'], 180)
            self.assertEqual({k:before[k] for k in KEYS}, {k:self.snap(p)[k] for k in KEYS})
            p.get_by_role('button', name='Voltar aos controles', exact=True).click()
            self.assertTrue(p.locator('#scene-result').evaluate('e=>document.activeElement===e'))
        finally: p.close()

    def test_08_reading_links_use_exact_base_part_ids(self):
        p = self.page()
        try:
            self.load(p, '?system=respiratory')
            data = json.loads((ROOT/'site/assets/respiratory/theory.json').read_text())
            part = 'resp_left_main_bronchus'
            p.evaluate('(id)=>heartViewer.select(id)', part)
            expected = {c['id'] for c in data['chapters'] if part in c.get('partIds', [])}
            self.assertTrue(expected)
            self.assertEqual(p.locator('#reading-context').count(), 1, 'No contextual reading access in the 3D inspector')
            p.wait_for_function('document.querySelectorAll("#reading-context a[data-chapter]").length>0')
            links = p.locator('#reading-context a[data-chapter]').evaluate_all('es=>es.map(e=>({id:e.dataset.chapter,href:e.href}))')
            self.assertEqual({a['id'] for a in links}, expected)
            p.locator('#reading-context a[data-chapter]').first.click()
            p.wait_for_selector('.chapter-title')
            self.assertIn('system=respiratory', p.url)
            self.assertIn('chapter=', p.url)
        finally: p.close()

    def test_09_all_four_runtime_queues_and_saved_ambiguous_session(self):
        sets = {'bp_FMA3895', 'hra_mitral', 'hra_tricuspid', 'hra_aortic', 'hra_pulmonary'}
        reports = []
        for name, query, catpath, count in MODELS:
            p = self.page(390)
            try:
                catalog = json.loads((ROOT/'site/assets'/catpath).read_text())
                forbidden = {x['id'] for x in catalog['parts'] if x.get('representation') in ['aggregate','ambiguous'] or x.get('quizEligible') is False or x['id'] in sets}
                key = 'atlas:practice:v3:' + {'heart':'circulatory','hra':'heart-hra'}.get(name,name)
                self.load(p, query)
                for mode in ['identify', 'find']:
                    p.locator('.study-launch').click()
                    self.assertIn('conjuntos agregados', p.locator('#study-setup').inner_text())
                    p.select_option('#study-mode', mode)
                    p.select_option('#study-group', 'all')
                    p.locator('#study-setup button[type="submit"]').click()
                    queue = p.evaluate('(key)=>JSON.parse(localStorage.getItem(key)).session.queue', key)
                    self.assertTrue(queue)
                    self.assertFalse(forbidden.intersection(queue), f'{name}/{mode}: excluded IDs entered runtime queue')
                    reports.append({'model':name, 'mode':mode, 'queue':queue, 'forbidden':sorted(forbidden)})
                    p.get_by_role('button',name='Pausar e explorar',exact=True).click()
                excluded = next(iter(forbidden))
                allowed = queue[0]
                p.evaluate('''({key,excluded,allowed})=>localStorage.setItem(key,JSON.stringify({version:2,ratings:{},session:{mode:'identify',group:'all',queue:[excluded,allowed],done:[],total:2}}))''', {'key':key,'excluded':excluded,'allowed':allowed})
                self.load(p, query)
                p.locator('.study-launch').click()
                p.get_by_role('button',name='Continuar · 1 restante',exact=True).click()
                # study.js sanitizes restored sessions in memory; it persists on the next answer,
                # not on opening/resuming. Old storage bytes are not the active runtime queue.
                self.assertEqual(p.evaluate('heartStudy.snapshot().remaining'), 1)
                self.assertEqual(self.snap(p)['selected'], allowed)
                p.get_by_role('button',name='Pausar e explorar',exact=True).click()
                p.evaluate('(id)=>heartViewer.select(id)', excluded)
                self.assertEqual(self.snap(p)['selected'], excluded)
                self.assertRegex(p.locator('#selection-policy').inner_text(), 'fora|não aprovada')
            finally: p.close()
        self.save('runtime-policy', reports)

    def test_10_selected_label_priority_and_curated_targets(self):
        for width in [1440,390]:
            for name, query, catpath, _ in MODELS:
                p = self.page(width)
                try:
                    self.load(p, query)
                    part = self.snap(p)['visibleParts'][0]
                    p.evaluate('(id)=>{heartViewer.select(id);heartViewer.focus(id);heartViewer.labels(true)}', part)
                    p.wait_for_timeout(700)
                    self.assertTrue(p.locator(f'.mesh-label[data-part-id="{part}"]').is_visible())
                    self.assert_label_layout(p)
                    self.assertIn('omitidos', p.locator('#label-status').inner_text())
                    if name == 'respiratory':
                        p.select_option('#study-view', 'arvore_superior_direito')
                        p.wait_for_timeout(700)
                        ids = [a['id'] for a in self.assert_label_layout(p)]
                        self.assertTrue(any('bronchus' in id for id in ids), f'No bronchial target labels: {ids}')
                    if name in ['hra','larynx']:
                        p.evaluate('(id)=>heartViewer.select(id)', part)
                        self.assertIn('Sem correspondência exata', p.locator('#reading-context').inner_text())
                        self.assertEqual(p.locator('#reading-context a[data-chapter]').count(), 0)
                    self.capture(p, f'fixed-labels-{name}-{width}', True)
                    if name == 'hra':
                        p.locator('[data-preset="valvas"]').click()
                        p.wait_for_timeout(700)
                        valve_labels = self.assert_label_layout(p)
                        self.assertTrue(valve_labels, 'Curated HRA valve view has no target labels')
                        self.assertTrue(any(a['id'] in ['hra_mitral','hra_tricuspid','hra_aortic','hra_pulmonary'] for a in valve_labels))
                finally: p.close()

    def test_11_left_b7_b8_variant_not_an_individual_quiz_answer(self):
        ids = ['resp_medial_basal_segmental_bronchus_of_left_lung_bvii', 'resp_anterior_basal_segmental_bronchus_of_left_lung_bviii']
        p = self.page(390)
        try:
            self.load(p, '?system=respiratory')
            for mode in ['identify','find']:
                p.locator('.study-launch').click()
                p.select_option('#study-mode', mode)
                p.select_option('#study-group', 'all')
                p.locator('#study-setup button[type="submit"]').click()
                queue = p.evaluate('JSON.parse(localStorage.getItem("atlas:practice:v3:respiratory")).session.queue')
                self.assertFalse(set(ids).intersection(queue), 'B7/B8 left variant unresolved: must stay outside context-free individual identification/find')
                p.get_by_role('button', name='Pausar e explorar', exact=True).click()
            for id in ids:
                p.evaluate('(id)=>heartViewer.select(id)', id)
                self.assertEqual(self.snap(p)['selected'], id)
                self.assertIn('variante', p.locator('#selection-policy').inner_text())
        finally: p.close()

if __name__ == '__main__':
    unittest.main()
