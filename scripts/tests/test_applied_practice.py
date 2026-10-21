"""Use actual source-grounded case data, no fabricated backend responses."""
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from test_exam_path import BASE

ROOT = Path(__file__).resolve().parents[2]

class AppliedCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        self.context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else route.abort())
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def test_all_source_grounded_cases_reveal_answer_explanation_and_rubric(self):
        cases = json.loads((ROOT / 'site/assets/study-cases.json').read_text())['cases']
        response = self.page.goto(BASE + '/practice.html')
        self.assertEqual(response.status, 200, 'Applied practice page must exist')
        self.page.wait_for_selector('#case-title')
        for case in cases:
            with self.subTest(case=case['id']):
                self.assertEqual(self.page.locator('#case-title').inner_text(), case['title'])
                self.assertEqual(self.page.locator('#case-answer').count(), 0)
                self.assertIn(case['scenario'], self.page.locator('#case-scenario').inner_text())
                self.page.get_by_role('button', name='Conferir raciocínio', exact=True).click()
                revealed = self.page.locator('#case-answer').inner_text()
                self.assertIn(case['answer'], revealed)
                self.assertIn(case['explanation'], revealed)
                for point in case['checkpoints']:
                    self.assertIn(point, revealed)
                self.assertGreater(self.page.locator('#case-answer .source-links').inner_text().__len__(), 20)
                self.page.get_by_role('button', name='Próximo caso', exact=True).click()

    def test_draft_and_review_mark_survive_reload_without_claiming_auto_grading(self):
        self.page.goto(BASE + '/practice.html')
        self.page.wait_for_selector('#case-draft')
        self.page.get_by_label('Explique em voz alta ou escreva seu raciocínio').fill('O líquido está fora das câmaras, entre as lâminas serosas.')
        self.page.reload()
        self.page.wait_for_selector('#case-draft')
        self.assertIn('lâminas serosas', self.page.locator('#case-draft').input_value())
        self.page.get_by_role('button', name='Conferir raciocínio', exact=True).click()
        self.page.get_by_role('button', name='Preciso retomar este caso', exact=True).click()
        self.assertIn('1 para retomar', self.page.locator('#case-progress').inner_text())
        self.page.reload()
        self.page.wait_for_selector('#case-title')
        self.assertIn('1 para retomar', self.page.locator('#case-progress').inner_text())
        self.assertEqual(self.page.locator('#case-answer').count(), 0)
        self.page.get_by_role('button', name='Conferir raciocínio', exact=True).click()
        self.page.get_by_role('button', name='Consegui justificar os pontos', exact=True).click()
        self.assertIn('0 para retomar', self.page.locator('#case-progress').inner_text())
        self.page.locator('#case-system').select_option('respiratory')
        self.assertEqual(self.page.locator('#case-list button').count(), 3)
        self.assertIn('A sensação falha', self.page.locator('#case-title').inner_text())
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_missing_case_data_has_an_honest_error(self):
        self.page.route('**/assets/study-cases.json', lambda route: route.fulfill(status=503, body='unavailable'))
        self.page.goto(BASE + '/practice.html')
        self.page.get_by_role('heading', name='Treino indisponível', exact=True).wait_for()
        self.assertIn('não carregado', self.page.locator('#case-progress').inner_text())

    def test_case_is_reachable_from_its_theory_chapter_and_home(self):
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-pericardio')
        self.page.wait_for_selector('.chapter-title')
        self.page.get_by_role('link', name='Praticar esta unidade', exact=True).click()
        self.page.wait_for_selector('#review-body h2')
        self.page.locator('#applied-link').click()
        self.page.wait_for_selector('#case-title')
        self.assertIn('enchimento limitado', self.page.locator('#case-title').inner_text())
        self.page.goto(BASE + '/index.html')
        self.page.wait_for_selector('.global-nav')
        for target in ['practice.html', 'search.html']:
            self.assertEqual(self.page.locator(f'.global-nav a[href="{target}"]').count(), 1)
            self.assertGreater(self.page.locator(f'main a[href="{target}"]').count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
