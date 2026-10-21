"""Chromium search acceptance using real chapter content in the agreed index contract."""
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from test_exam_path import BASE

ROOT = Path(__file__).resolve().parents[2]

class FrontSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)
        cls.items = []
        for system, path in [('circulatory', 'circulatory-theory.json'), ('respiratory', 'respiratory/theory.json')]:
            for chapter in json.loads((ROOT / 'site/assets' / path).read_text())['chapters']:
                cls.items.append(dict(id=chapter['id'], system=system, chapterId=chapter['id'], title=chapter['title'], summary=chapter['summary'], text=json.dumps(chapter, ensure_ascii=False), url=f"theory.html?system={system}&chapter={chapter['id']}"))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 390, 'height': 844})
        self.context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(BASE) else r.abort())
        self.page = self.context.new_page()
        self.page.set_default_timeout(5000)

    def tearDown(self):
        self.context.close()

    def index(self, payload=None, status=200):
        self.page.route('**/assets/search-index.json', lambda r: r.fulfill(status=status, content_type='application/json', body=json.dumps(payload if payload is not None else {'version': 1, 'items': self.items})))

    def test_search_matches_accentless_terms_in_both_systems_and_opens_real_chapter(self):
        self.index()
        response = self.page.goto(BASE + '/search.html?q=valvas')
        self.assertEqual(response.status, 200, 'Search page must exist')
        self.page.locator('#search-results a').first.wait_for()
        self.assertIn('circulatory', self.page.locator('#search-results a').first.get_attribute('href'))
        self.page.get_by_label('Buscar nos dois sistemas').fill('respiratorio pleura')
        self.page.locator('#search-results a').first.wait_for()
        link = self.page.locator('#search-results a').first
        self.assertIn('respiratory', link.get_attribute('href'))
        target = link.get_attribute('href')
        link.click()
        self.page.wait_for_selector('.chapter-title')
        self.assertTrue(self.page.url.endswith(target))
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_unavailable_index_is_honest_and_links_to_both_real_theory_lists(self):
        self.index(status=404)
        self.page.goto(BASE + '/search.html?q=pleura')
        self.page.get_by_role('status').filter(has_text='indisponível').wait_for()
        self.assertEqual(self.page.locator('#search-results a').count(), 0)
        self.assertEqual(self.page.locator('#search-fallback a').count(), 2)

    def test_deployed_index_loads_and_resolves_chapters_without_page_errors(self):
        errors = []
        self.page.on('pageerror', lambda error: errors.append(str(error)))
        index_response = self.page.request.get(BASE + '/assets/search-index.json')
        self.assertEqual(index_response.status, 200, 'Backend must generate the deployed index before release')
        index = index_response.json()
        self.assertEqual(index['version'], 1)
        for term, system in [('valvas', 'circulatory'), ('pleura', 'respiratory')]:
            self.page.goto(BASE + '/search.html?q=' + term)
            self.page.locator('#search-results a').first.wait_for()
            self.assertTrue(any('system=' + system in href for href in self.page.locator('#search-results a').evaluate_all('(nodes) => nodes.map(n => n.href)')))
        self.assertEqual(errors, [])

    def test_no_matches_and_system_filter_are_accessible(self):
        self.index()
        self.page.goto(BASE + '/search.html?q=pleura')
        self.page.locator('#search-results a').first.wait_for()
        self.page.get_by_label('Sistema', exact=True).select_option('respiratory')
        for href in self.page.locator('#search-results a').evaluate_all('(nodes) => nodes.map(n => n.href)'):
            self.assertIn('system=respiratory', href)
        self.page.get_by_label('Buscar nos dois sistemas').fill('zzzzsemresultados')
        self.page.get_by_role('status').filter(has_text='Nenhum resultado').wait_for()
        self.assertEqual(self.page.locator('#search-results a').count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
