"""Fast negative controls for the layout guard used by real 3D screenshots."""
import unittest
from playwright.sync_api import sync_playwright
from scripts.tests.test_3d_study import assert_viewer_layout_stable


class ViewerLayoutGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.page.set_content('<div id="viewer" style="width:500px;height:680px"></div>')

    def tearDown(self):
        self.page.close()

    def test_stable_layout_is_accepted(self):
        self.assertEqual(assert_viewer_layout_stable(self.page), [8, 8, 500, 680])

    def test_oscillating_size_is_rejected(self):
        self.page.evaluate('''() => {
          let frame = 0;
          function oscillate() {
            document.querySelector('#viewer').style.height = (++frame % 2 ? 680 : 682) + 'px';
            requestAnimationFrame(oscillate);
          }
          requestAnimationFrame(oscillate);
        }''')
        with self.assertRaisesRegex(AssertionError, 'oscillates on height'):
            assert_viewer_layout_stable(self.page)

    def test_moving_position_is_rejected(self):
        self.page.evaluate('''() => {
          let frame = 0;
          function oscillate() {
            document.querySelector('#viewer').style.transform = `translateY(${++frame % 2}px)`;
            requestAnimationFrame(oscillate);
          }
          requestAnimationFrame(oscillate);
        }''')
        with self.assertRaisesRegex(AssertionError, 'oscillates on y'):
            assert_viewer_layout_stable(self.page)


if __name__ == '__main__':
    unittest.main()
