"""Regression: retired case entry points leave theory and recognition intact."""
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from test_exam_path import BASE

ROOT = Path(__file__).resolve().parents[2]

class RetiredAppliedPracticeTests(unittest.TestCase):
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
        self.context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(BASE) else r.abort())
        self.page = self.context.new_page()
        self.errors, self.requests = [], []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('request', lambda r: self.requests.append(r.url))

    def tearDown(self):
        self.context.close()

    def test_home_and_exercises_have_no_case_entry_points(self):
        for width in [1280, 390]:
            self.page.set_viewport_size({'width': width, 'height': 900})
            for path in ['index.html', 'exercises.html']:
                with self.subTest(width=width, path=path):
                    self.page.goto(BASE + '/' + path)
                    self.page.wait_for_selector('.global-nav')
                    if path == 'exercises.html':
                        self.page.wait_for_selector('#review-body h2')
                        self.assertTrue(self.page.locator('#recognition-link').is_visible())
                    self.assertEqual(self.page.locator('a[href*="practice.html"], #applied-link').count(), 0)
                    self.assertNotIn('casos', self.page.locator('body').inner_text().lower())
                    self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.assertEqual(self.errors, [])
        self.assertFalse(any('study-cases.json' in u for u in self.requests))

    def test_shared_navigation_on_all_top_level_entrypoints(self):
        entrypoints = sorted(p.name for p in (ROOT / 'site').glob('*.html') if p.name != 'practice.html')
        for path in entrypoints:
            with self.subTest(path=path):
                self.page.goto(BASE + '/' + path, wait_until='domcontentloaded')
                # All normal site pages use the same navigation module.
                if 'navigation.js' in (ROOT / 'site' / path).read_text():
                    self.page.wait_for_selector('.global-nav')
                    self.assertEqual(self.page.locator('a[href*="practice.html"]').count(), 0)
        self.assertFalse(any('study-cases.json' in u for u in self.requests))

    def test_every_chapter_links_to_exercises_without_cases(self):
        visited = []
        for system, filename in [('circulatory', 'circulatory-theory.json'), ('respiratory', 'respiratory/theory.json')]:
            chapters = json.loads((ROOT / 'site/assets' / filename).read_text())['chapters']
            for chapter in chapters:
                with self.subTest(system=system, chapter=chapter['id']):
                    self.page.goto(BASE + '/theory.html?system=' + system + '&chapter=' + chapter['id'])
                    self.page.wait_for_selector('.chapter-title')
                    self.assertEqual(self.page.locator('a[href*="practice.html"]').count(), 0)
                    self.page.get_by_role('link', name='Praticar esta unidade', exact=True).click()
                    self.page.wait_for_selector('#review-body h2')
                    self.assertEqual(self.page.locator('#exercise-chapter').input_value(), chapter['id'])
                    self.assertEqual(self.page.locator('#applied-link').count(), 0)
                    visited.append((system, chapter['id']))
        self.assertEqual(len(visited), len(set(visited)))
        self.assertEqual(self.errors, [])
        self.assertFalse(any('study-cases.json' in u for u in self.requests))

    def test_legacy_bookmarks_redirect_with_context_without_loading_cases(self):
        for query, system, chapter in [('', 'circulatory', ''),
                ('?system=circulatory&chapter=circ-pericardio&case=old', 'circulatory', 'circ-pericardio'),
                ('?system=respiratory&chapter=resp_06#old-case', 'respiratory', 'resp_06')]:
            with self.subTest(query=query):
                self.page.goto(BASE + '/practice.html' + query)
                self.page.wait_for_url('**/exercises.html*', timeout=3000)
                self.page.wait_for_selector('#review-body h2')
                self.assertEqual(self.page.locator('#exercise-system').input_value(), system)
                self.assertEqual(self.page.locator('#exercise-chapter').input_value(), chapter)
                self.assertNotIn('case=', self.page.url)
                self.assertNotIn('#', self.page.url)
        self.assertFalse(any('study-cases.json' in u for u in self.requests))
        self.assertEqual(self.errors, [])

    def test_legacy_page_has_fallback_without_javascript(self):
        with self.browser.new_context(java_script_enabled=False) as context:
            page = context.new_page()
            page.goto(BASE + '/practice.html?system=respiratory&chapter=resp_06')
            link = page.get_by_role('link', name='Abrir exercícios', exact=True)
            self.assertTrue(link.is_visible())
            self.assertEqual(link.get_attribute('href'), 'exercises.html')

if __name__ == '__main__':
    unittest.main(verbosity=2)
