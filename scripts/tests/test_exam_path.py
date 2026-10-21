"""Browser acceptance tests. Run with a local static server on port 8876."""
import os
import unittest
from playwright.sync_api import sync_playwright

BASE = os.environ.get('ATLAS_TEST_URL', 'http://127.0.0.1:8876')

class ExamPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

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

    def test_learning_path_loads_a_single_topic_with_real_theory_links(self):
        response = self.page.goto(BASE + '/prova.html')
        self.assertEqual(response.status, 200, 'Learning path must exist')
        self.page.wait_for_selector('#topic-title')
        self.assertIn('percurso do sangue', self.page.locator('#topic-title').inner_text().lower())
        self.assertGreater(self.page.locator('#topic-links a').count(), 0)
        self.assertEqual(self.page.locator('#path-list button[aria-current="step"]').count(), 1)
        self.assertIn('não confirma', self.page.locator('#scope-note').inner_text().lower())

    def test_reveal_rate_and_reload_keep_question_records(self):
        self.page.goto(BASE + '/prova.html')
        self.page.wait_for_selector('#topic-title')
        self.assertEqual(self.page.locator('#question-title').count(), 1, 'Topic must offer a recall question')
        self.assertEqual(self.page.locator('#question-answer').count(), 0)
        self.page.get_by_role('button', name='Conferir resposta', exact=True).click()
        self.assertGreater(len(self.page.locator('#question-answer').inner_text()), 40)
        self.page.get_by_role('button', name='Preciso rever', exact=True).click()
        self.assertIn('1 de 3', self.page.locator('#topic-progress').inner_text())
        self.page.reload()
        self.assertIn('1 de 3', self.page.locator('#topic-progress').inner_text())
        self.assertEqual(self.page.locator('#question-answer').count(), 0)
        self.assertIn('retornar', self.page.locator('#question-title').inner_text())
        self.page.get_by_role('button', name='Conferir resposta', exact=True).click()
        self.page.get_by_role('button', name='Consegui explicar', exact=True).click()
        self.assertIn('0 para retomar', self.page.locator('#path-progress').inner_text())
        self.page.get_by_role('button', name='Próxima pergunta', exact=True).click()
        self.assertNotIn('retornar', self.page.locator('#question-title').inner_text())

    def test_path_is_discoverable_from_home_and_theory(self):
        for route in ['/index.html', '/theory.html']:
            with self.subTest(route=route):
                self.page.goto(BASE + route)
                self.page.wait_for_selector('.global-nav')
                self.assertEqual(self.page.locator('.global-nav a[href="prova.html"]').count(), 1)
                self.assertGreater(self.page.locator('main a[href="prova.html"]').count(), 0)

    def test_mobile_topic_navigation_has_no_overflow(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        errors = []
        self.page.on('pageerror', lambda error: errors.append(str(error)))
        self.page.goto(BASE + '/prova.html?topic=pleura')
        self.page.wait_for_selector('#topic-title')
        self.assertIn('tórax', self.page.locator('#topic-title').inner_text())
        self.assertLess(self.page.locator('#topic-title').bounding_box()['y'], 844, 'Mobile must show the concept before the first full scroll')
        self.page.get_by_role('button', name='Escolher outro tema', exact=True).click()
        self.assertTrue(self.page.locator('#path-list').is_visible())
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        for item in self.page.locator('#path-list button').all():
            if not item.is_visible():
                self.page.get_by_role('button', name='Escolher outro tema', exact=True).click()
            item.click()
            self.assertEqual(self.page.locator('#question-title').count(), 1)
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.assertEqual(errors, [])

    def test_bad_or_blocked_storage_does_not_prevent_review(self):
        for script in ["localStorage.setItem('atlas:exam-path:v1', '{bad')", "Object.defineProperty(window, 'localStorage', {get(){throw new Error('blocked')}})"]:
            with self.subTest(script=script):
                context = self.browser.new_context()
                context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else route.abort())
                context.add_init_script(script)
                page = context.new_page()
                page.goto(BASE + '/prova.html?topic=coronarias')
                page.wait_for_selector('#question-title')
                page.get_by_role('button', name='Conferir resposta', exact=True).click()
                page.get_by_role('button', name='Preciso rever', exact=True).click()
                self.assertIn('1 de 3', page.locator('#topic-progress').inner_text())
                context.close()

    def test_missing_data_shows_clear_error_instead_of_empty_page(self):
        self.page.route('**/assets/exam-path.json', lambda route: route.fulfill(status=503, body='unavailable'))
        self.page.goto(BASE + '/prova.html')
        self.page.get_by_role('heading', name='Percurso indisponível', exact=True).wait_for()
        self.assertIn('não carregado', self.page.locator('#path-progress').inner_text())

if __name__ == '__main__':
    unittest.main(verbosity=2)
