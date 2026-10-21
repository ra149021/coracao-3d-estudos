"""Focused real Chromium persistence tests; no WebGL or personal storage."""
import os
import unittest
from playwright.sync_api import sync_playwright

BASE = os.environ.get('ATLAS_BASE_URL', 'http://127.0.0.1:8878')


class PersistenceRegressions(unittest.TestCase):
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
        self.page = self.context.new_page()
        self.page.goto(BASE + '/prova.html')
        self.page.wait_for_selector('#question-title')
        self.page.evaluate('''() => {
          window.rawGet = Storage.prototype.getItem;
          window.rawSet = Storage.prototype.setItem;
          window.failRead = false; window.failWrite = false; window.writes = 0;
          Storage.prototype.getItem = function(k) { if(window.failRead) throw Error('read denied'); return rawGet.call(this,k); };
          Storage.prototype.setItem = function(k,v) { if(window.failWrite) throw Error('write denied'); window.writes++; return rawSet.call(this,k,v); };
        }''')

    def tearDown(self):
        self.context.close()

    def seed(self, key, value):
        self.page.evaluate('([k,v]) => rawSet.call(localStorage,k,JSON.stringify(v))', [key, value])

    def read(self, key):
        return self.page.evaluate('(k) => JSON.parse(rawGet.call(localStorage,k))', key)

    def study(self):
        self.page.evaluate('''async () => {
          const {initStudy} = await import('./study.js');
          const viewer = new Proxy({}, {get: (_, key) => key === 'snapshot' ? () => ({}) : () => {}});
          initStudy({viewer, parts: ['a','b'].map(id => ({id,label:id,group:'camaras',triangles:1}))});
          heartStudy.openPractice();
        }''')
        self.page.get_by_role('button', name='Começar rodada', exact=True).click()

    def test_study_read_failure_preserves_bytes_then_recovers(self):
        key = 'atlas:practice:v3:circulatory'
        original = {'version': 2, 'ratings': {'other': {'rating': 'review'}}, 'extension': {'safe': True}, 'session': None}
        self.seed(key, original)
        self.page.evaluate('window.failRead = true')
        self.study()
        self.assertEqual(self.read(key), original)
        self.assertEqual(self.page.evaluate('window.writes'), 0)
        self.assertIn('sessão', self.page.locator('.study-session').inner_text())
        self.page.evaluate('window.failRead = false')
        original['ratings']['remote'] = {'rating': 'known'}
        self.seed(key, original)
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Identifiquei com segurança').click()
        saved = self.read(key)
        self.assertEqual(saved['extension'], original['extension'])
        self.assertEqual(saved['ratings']['remote'], {'rating': 'known'})
        self.assertEqual(saved['ratings']['other'], {'rating': 'review'})
        self.assertEqual(len(saved['session']['done']), 1)

    def test_prova_merges_other_tab_and_extension(self):
        key = 'atlas:exam-path:v1'
        self.seed(key, {'remote:q': 'review', 'extension': {'safe': True}})
        self.page.get_by_role('button', name='Conferir resposta').click()
        self.page.get_by_role('button', name='Consegui explicar').click()
        saved = self.read(key)
        self.assertEqual(saved.get('remote:q'), 'review')
        self.assertEqual(saved.get('extension'), {'safe': True})

    def test_prova_pending_recovery_and_stale_map(self):
        key = 'atlas:exam-path:v1'
        self.page.get_by_role('button', name='Conferir resposta').click()
        self.page.evaluate('window.failRead = true')
        self.page.get_by_role('button', name='Consegui explicar').click()
        self.assertEqual(self.page.evaluate('window.writes'), 0)
        self.assertIn('sessão', self.page.locator('#save-status').inner_text())
        self.page.get_by_role('button', name='Próxima pergunta').click()
        self.page.get_by_role('button', name='Conferir resposta').click()
        self.page.evaluate('window.failRead = false; window.failWrite = true')
        self.seed(key, {'remote:q': 'known', 'extension': {'safe': True}})
        self.page.get_by_role('button', name='Preciso rever', exact=True).click()
        self.assertEqual(len(self.read(key)), 2)
        self.page.evaluate('window.failWrite = false')
        self.page.get_by_role('button', name='Preciso rever', exact=True).click()
        saved = self.read(key)
        self.assertEqual(len(saved), 4)
        self.assertEqual(saved['remote:q'], 'known')
        first = next(k for k,v in saved.items() if k != 'remote:q' and v == 'known')
        saved[first] = 'review'  # A newer update must not be reverted by a later save.
        self.seed(key, saved)
        self.page.get_by_role('button', name='Consegui explicar').click()
        self.assertEqual(self.read(key)[first], 'review')
        self.assertIn('salva', self.page.locator('#save-status').inner_text())

    def test_study_pending_write_merges_record_fields_and_pause(self):
        key = 'atlas:practice:v3:circulatory'
        self.seed(key, {'version': 2, 'ratings': {}, 'session': None})
        self.study()
        target = self.read(key)['session']['queue'][0]
        self.page.evaluate('window.failWrite = true')
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Identifiquei com segurança').click()
        self.assertIn('sessão', self.page.locator('.study-session').inner_text())
        latest = self.read(key)
        latest['ratings'] = {target: {'rating': 'review', 'attempts': 7, 'extension': 'keep'}, 'remote': {'rating': 'review'}}
        latest['session']['extension'] = 'session-keep'
        latest['extension'] = 'root-keep'
        self.seed(key, latest)
        self.page.evaluate('window.failWrite = false')
        self.page.get_by_role('button', name='Pausar e explorar').click()
        saved = self.read(key)
        self.assertEqual(saved['ratings'][target]['attempts'], 8)
        self.assertEqual(saved['ratings'][target]['extension'], 'keep')
        self.assertEqual(saved['ratings'][target]['rating'], 'known')
        self.assertEqual(saved['ratings']['remote']['rating'], 'review')
        self.assertEqual(saved['session']['extension'], 'session-keep')
        self.assertEqual(saved['extension'], 'root-keep')
        self.assertEqual(len(saved['session']['done']), 1)
        # Pausing without a local mutation must not replay an old session or rating.
        saved['session']['extension'] = 'newer'
        saved['ratings'][target]['rating'] = 'review'
        self.seed(key, saved)
        self.page.evaluate('heartStudy.openPractice()')
        self.page.get_by_role('button', name='Continuar · 1 restante', exact=True).click()
        self.page.get_by_role('button', name='Pausar e explorar').click()
        self.assertEqual(self.read(key), saved)

    def test_malformed_stores_are_not_replaced(self):
        for raw in ['{bad', '[]', 'null', '']:
            with self.subTest(raw=raw):
                self.page.evaluate('(raw) => rawSet.call(localStorage,"atlas:exam-path:v1",raw)', raw)
                if self.page.get_by_role('button', name='Conferir resposta').count():
                    self.page.get_by_role('button', name='Conferir resposta').click()
                self.page.get_by_role('button', name='Consegui explicar').click()
                self.assertEqual(self.page.evaluate('rawGet.call(localStorage,"atlas:exam-path:v1")'), raw)
        self.page.evaluate('rawSet.call(localStorage,"atlas:practice:v3:circulatory","{bad")')
        self.study()
        self.assertEqual(self.page.evaluate('rawGet.call(localStorage,"atlas:practice:v3:circulatory")'), '{bad')
        self.assertIn('sessão', self.page.locator('.study-session').inner_text())


if __name__ == '__main__':
    unittest.main()
