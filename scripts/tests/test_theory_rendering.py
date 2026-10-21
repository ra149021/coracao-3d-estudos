"""Exercise every theory chapter and reveal every answer in Chromium."""
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from test_exam_path import BASE

ROOT = Path(__file__).resolve().parents[2]

class TheoryRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else route.abort())
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()
    def test_every_chapter_and_answer_renders(self):
        errors = []
        self.page.on('pageerror', lambda error: errors.append(str(error)))
        chapters_checked = questions_checked = 0
        for system, filename in [('circulatory', 'assets/circulatory-theory.json'), ('respiratory', 'assets/respiratory/theory.json')]:
            data = json.loads((ROOT / 'site' / filename).read_text())
            for chapter in data['chapters']:
                with self.subTest(system=system, chapter=chapter['id']):
                    self.page.goto(f"{BASE}/theory.html?system={system}&chapter={chapter['id']}")
                    self.page.wait_for_selector('.chapter-title')
                    self.assertEqual(self.page.locator('.chapter-title').inner_text(), chapter['title'])
                    self.assertEqual(self.page.locator('.lesson-section').count(), len(chapter['sections']))
                    chapters_checked += 1
                    self.assertEqual(self.page.locator('#review-dialog').count(), 0)
                    self.page.get_by_role('link', name='Praticar esta unidade', exact=True).click()
                    self.page.wait_for_selector('#review-body h2')
                    for question in chapter['recall']:
                        self.assertEqual(self.page.locator('#review-body h2').inner_text(), question['question'])
                        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
                        self.assertIn(question['answer'], self.page.locator('.recall-answer').inner_text())
                        self.assertIn(question['explanation'], self.page.locator('.recall-answer').inner_text())
                        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
                        questions_checked += 1
                    self.assertEqual(self.page.locator('#review-body h2').inner_text(), 'Rodada concluída')
        self.assertEqual(errors, [])
        print(json.dumps({'chapters_rendered': chapters_checked, 'answers_revealed': questions_checked, 'page_errors': errors}))

if __name__ == '__main__':
    unittest.main(verbosity=2)
