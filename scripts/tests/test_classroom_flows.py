"""Real Chromium classroom flows; no external video downloads.
Run: atlas-qa-venv/bin/python -m unittest discover -s scripts/tests -p test_classroom_flows.py -v
"""
import os
import unittest
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('ATLAS_TEST_URL', 'http://127.0.0.1:8876')


class ClassroomFlowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1100, 'height': 850})
        # Exercise actual static assets; never download the full remote videos.
        self.context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else route.abort())
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def open(self, query=''):
        self.page.goto(BASE + '/classroom.html' + query)
        self.page.wait_for_selector('#material-title h2')

    def loaded_slide(self):
        expect(self.page.locator('.slide-frame img')).to_be_visible()
        self.page.wait_for_function("document.querySelector('.slide-frame img')?.naturalWidth > 0")

    def test_default_prefers_real_slide_document_over_online_video(self):
        self.open()
        expect(self.page.locator('.slide-frame img')).to_be_visible(timeout=2000)
        self.loaded_slide()
        self.assertEqual(self.page.locator('video').count(), 0)
        self.assertIn('doc=', self.page.url)

    def test_embed_hides_shell_but_preserves_document_and_video_study_controls(self):
        self.open('?doc=coracao&page=3&embed=1')
        self.loaded_slide()
        for selector in ('.global-nav', '.classroom-heading', '.page-footer', '.library-sidebar', '.skip-link'):
            expect(self.page.locator(selector)).to_be_hidden(timeout=1500)
        expect(self.page.locator('#material-title h2')).to_have_text('Coração')
        self.page.get_by_role('button', name='Próxima página', exact=True).click()
        expect(self.page.get_by_role('spinbutton', name='Número da página')).to_have_value('4')
        self.assertIn('embed=1', self.page.url)
        self.page.reload()
        self.loaded_slide()
        expect(self.page.locator('.library-sidebar')).to_be_hidden()
        self.open('?video=R1&t=59&embed=1')
        expect(self.page.locator('video')).to_be_visible()
        expect(self.page.get_by_role('combobox', name='Velocidade da aula')).to_be_visible()
        search = self.page.get_by_role('searchbox', name='Buscar na transcrição')
        expect(search).to_be_visible()
        expect(self.page.locator('.transcript-line').first).to_be_visible()
        search.fill('zzzz_no_match')
        expect(self.page.locator('.transcript-count')).to_contain_text('0 de')
        self.assertIn('t=59', self.page.url)
        self.assertIn('embed=1', self.page.url)
        self.open('?doc=coracao')
        for selector in ('.global-nav', '.classroom-heading', '.page-footer', '.library-sidebar'):
            expect(self.page.locator(selector)).to_be_visible()

    def test_document_zoom_enlarges_scrollable_image_and_original_link_is_real(self):
        self.page.set_viewport_size({'width': 480, 'height': 800})
        self.open('?doc=coracao&page=2&embed=1')
        self.loaded_slide()
        image = self.page.locator('.slide-frame img')
        fit_width = image.bounding_box()['width']
        zoom = self.page.get_by_role('combobox', name='Zoom do documento')
        expect(zoom).to_be_visible(timeout=1500)
        zoom.select_option('2')
        self.assertGreater(image.bounding_box()['width'], fit_width * 1.8)
        self.assertTrue(self.page.locator('.slide-frame').evaluate('(n) => n.scrollWidth > n.clientWidth'))
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 480)
        original = self.page.get_by_role('link', name='Abrir imagem original', exact=False)
        self.assertEqual(original.get_attribute('href'), image.get_attribute('src'))
        self.assertEqual(original.get_attribute('target'), '_blank')
        response = self.context.request.get(BASE + '/' + original.get_attribute('href'))
        self.assertEqual(response.status, 200)
        self.assertIn('image/jpeg', response.headers.get('content-type', ''))
        self.page.get_by_role('button', name='Próxima página', exact=True).click()
        expect(zoom).to_have_value('2')
        zoom.select_option('fit')
        self.loaded_slide()
        self.assertLessEqual(image.bounding_box()['width'], fit_width + 1)

    def test_library_restores_per_document_page_but_explicit_page_overrides(self):
        self.open('?doc=coracao&page=7')
        self.loaded_slide()
        self.page.get_by_role('button', name='Próxima página', exact=True).click()
        self.page.locator('.material-button').filter(has_text='Vasos sanguíneos').click()
        number = self.page.get_by_role('spinbutton', name='Número da página')
        number.fill('12')
        number.press('Tab')
        self.page.locator('.material-button').filter(has_text='Coração').click()
        expect(number).to_have_value('8', timeout=1500)
        self.page.locator('.material-button').filter(has_text='Vasos sanguíneos').click()
        expect(number).to_have_value('12')
        self.open('?doc=coracao')
        expect(number).to_have_value('8')
        self.open('?doc=coracao&page=2')
        expect(number).to_have_value('2')
        self.open('?doc=coracao')
        expect(number).to_have_value('2')
        self.open('?doc=coracao&page=9999')
        expect(number).to_have_value('75')
        expect(self.page.get_by_role('button', name='Próxima página', exact=True)).to_be_disabled()
        self.open('?doc=coracao&page=-9')
        expect(number).to_have_value('1')

    def test_embed_runs_in_an_actual_narrow_theory_iframe(self):
        self.page.goto(BASE + '/classroom.html?doc=coracao')
        self.page.evaluate("""() => {
            const frame = document.createElement('iframe');
            frame.id = 'source-test-frame'; frame.width = '420'; frame.height = '650';
            frame.src = 'classroom.html?doc=respiratorio&page=20&embed=1';
            document.body.replaceChildren(frame);
        }""")
        frame = self.page.frame_locator('#source-test-frame')
        expect(frame.locator('.slide-frame img')).to_be_visible()
        expect(frame.locator('.global-nav')).to_be_hidden()
        expect(frame.get_by_role('spinbutton', name='Número da página')).to_have_value('20')
        frame.get_by_role('combobox', name='Zoom do documento').select_option('2')
        self.assertTrue(frame.locator('.slide-frame').evaluate('(n) => n.scrollWidth > n.clientWidth'))
        frame.get_by_role('button', name='Próxima página', exact=True).click()
        expect(frame.get_by_role('spinbutton', name='Número da página')).to_have_value('21')

    def test_corrupt_storage_does_not_break_document_or_existing_video_controls(self):
        self.page.goto(BASE + '/classroom.html?doc=coracao')
        self.page.evaluate("""() => {
            localStorage.setItem('atlas:document-pages', '{broken');
            localStorage.setItem('atlas:lecture-positions', '{broken');
        }""")
        self.open('?doc=coracao')
        self.loaded_slide()
        self.open('?video=R1&t=59')
        speed = self.page.get_by_role('combobox', name='Velocidade da aula')
        speed.select_option('1.5')
        self.assertEqual(self.page.locator('video').evaluate('(v) => v.playbackRate'), 1.5)
        self.assertTrue(self.page.locator('video').evaluate('(v) => v.controls'))
        expect(self.page.get_by_role('button', name='← 10 s', exact=True)).to_be_visible()
        expect(self.page.get_by_role('button', name='10 s →', exact=True)).to_be_visible()
        expect(self.page.locator('.transcript-line').first).to_be_visible()


if __name__ == '__main__':
    unittest.main()
