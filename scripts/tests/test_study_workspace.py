"""Realistic reading workflows: figures, sources and personal study notes."""
import unittest
from playwright.sync_api import sync_playwright
from test_exam_path import BASE

class StudyWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1600, 'height': 1000}, accept_downloads=True)
        self.context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else route.abort())
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def test_actual_source_slides_are_available_beside_the_explanation(self):
        self.page.goto(BASE + '/theory.html?system=respiratory&chapter=resp_09')
        self.page.wait_for_selector('.chapter-title')
        self.assertGreater(self.page.locator('.lesson-section .lesson-figures').count(), 0, 'Sections need the cited source figures, not just links')
        figure = self.page.locator('.lesson-section .teaching-figure').first
        figure.scroll_into_view_if_needed()
        image = figure.locator('img')
        self.page.wait_for_function('(img) => img.complete && img.naturalWidth > 0', arg=image.element_handle())
        self.assertIn('assets/lectures/slides/respiratorio/', image.get_attribute('src'))
        gallery = self.page.locator('.lesson-figures').filter(has=self.page.locator('select')).first
        gallery.get_by_label('Comparar duas páginas').check()
        self.assertEqual(gallery.locator('.teaching-figure').count(), 2)

    def test_opening_a_source_keeps_the_explanation_and_restores_focus(self):
        self.page.goto(BASE + '/theory.html?system=respiratory&chapter=resp_09')
        self.page.wait_for_selector('.teaching-figure')
        trigger = self.page.locator('.figure-image-link').first
        trigger.click()
        self.assertIn('theory.html', self.page.url, 'Source must not replace the reading page')
        self.assertTrue(self.page.locator('#source-panel').is_visible())
        self.assertIn('embed=1', self.page.locator('#source-frame').get_attribute('src'))
        self.assertTrue(self.page.locator('.chapter-title').is_visible())
        frame = self.page.frame_locator('#source-frame')
        frame.locator('.slide-frame img').wait_for()
        self.page.wait_for_function("() => document.querySelector('#source-frame').contentDocument.querySelector('.slide-frame img')?.naturalWidth > 0")
        self.page.get_by_role('button', name='Fechar material e voltar à leitura', exact=True).click()
        self.assertFalse(self.page.locator('#source-panel').is_visible())
        self.assertEqual(self.page.locator('#source-frame').get_attribute('src'), 'about:blank')
        self.assertTrue(trigger.evaluate('(node) => node === document.activeElement'))

    def test_personal_notes_survive_topic_changes_reload_and_export(self):
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('.chapter-title')
        self.assertEqual(self.page.locator('#study-notes').count(), 1, 'Reading needs a personal notes field')
        self.page.locator('#study-notes-box').evaluate('(node) => node.open = true')
        text = 'Minha dúvida: por que as cordas não abrem a mitral?'
        self.page.get_by_label('Minhas dúvidas e explicações').fill(text)
        self.page.reload()
        self.page.wait_for_selector('#study-notes')
        self.assertEqual(self.page.locator('#study-notes').input_value(), text)
        self.page.locator('#chapter-list button').first.click()
        self.assertEqual(self.page.locator('#study-notes').input_value(), '')
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#study-notes')
        self.assertEqual(self.page.locator('#study-notes').input_value(), text)
        self.page.locator('#study-notes-box').evaluate('(node) => node.open = true')
        with self.page.expect_download() as download_info:
            self.page.get_by_role('button', name='Baixar minhas anotações', exact=True).click()
        from pathlib import Path
        exported = Path(download_info.value.path()).read_text()
        self.assertIn(text, exported)
        self.assertIn('Valvas e esqueleto fibroso', exported)

    def test_source_panel_changes_mode_on_resize_and_escape_restores_focus(self):
        self.page.goto(BASE + '/theory.html?system=respiratory&chapter=resp_09')
        trigger = self.page.locator('.figure-image-link').first
        trigger.click()
        self.assertFalse(self.page.locator('#source-panel').evaluate('(n) => n.matches(":modal")'))
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.page.wait_for_timeout(150)
        self.assertTrue(self.page.locator('#source-panel').evaluate('(n) => n.matches(":modal")'))
        self.assertFalse(self.page.locator('body').evaluate('(n) => n.classList.contains("study-source-open")'))
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.page.set_viewport_size({'width': 1600, 'height': 1000})
        self.page.wait_for_timeout(150)
        self.assertFalse(self.page.locator('#source-panel').evaluate('(n) => n.matches(":modal")'))
        self.page.keyboard.press('Escape')
        self.assertFalse(self.page.locator('#source-panel').is_visible())
        self.assertTrue(trigger.evaluate('(n) => n === document.activeElement'))

    def test_notes_and_resume_never_replace_existing_review_progress(self):
        original = {'read': {'circ-circuitos': True}, 'answers': {'existing-question': {'rating': 'review', 'at': 123}}}
        import json
        self.context.add_init_script(f"if (!localStorage.getItem('atlas:theory:circulatory')) localStorage.setItem('atlas:theory:circulatory', {json.dumps(json.dumps(original))});")
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('.chapter-title')
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.get_by_label('Minhas dúvidas e explicações').fill('Explicação circulatória')
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('atlas:theory:circulatory'))"), original)
        self.page.get_by_role('button', name='Marcar unidade como lida', exact=True).click()
        saved = self.page.evaluate("JSON.parse(localStorage.getItem('atlas:theory:circulatory'))")
        self.assertEqual(saved['answers'], original['answers'])
        self.assertTrue(saved['read']['circ-circuitos'])
        self.assertTrue(saved['read']['circ-valvas'])
        self.page.goto(BASE + '/theory.html?system=respiratory&chapter=resp_09')
        self.page.wait_for_selector('.chapter-title')
        self.assertEqual(self.page.locator('#study-notes').input_value(), '')
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.get_by_label('Minhas dúvidas e explicações').fill('Explicação respiratória')
        self.page.goto(BASE + '/theory.html?system=circulatory')
        self.page.wait_for_selector('.chapter-title')
        self.assertEqual(self.page.locator('#study-notes').input_value(), 'Explicação circulatória')

    def test_resume_is_per_system_and_explicit_chapter_wins(self):
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('.chapter-title')
        self.page.goto(BASE + '/theory.html?system=respiratory&chapter=resp_09')
        self.page.wait_for_selector('.chapter-title')
        self.page.goto(BASE + '/theory.html?system=circulatory')
        self.page.wait_for_selector('.chapter-title')
        self.assertIn('chapter=circ-valvas', self.page.url)
        self.page.goto(BASE + '/theory.html?system=respiratory')
        self.page.wait_for_selector('.chapter-title')
        self.assertIn('chapter=resp_09', self.page.url)
        self.page.goto(BASE + '/theory.html?system=respiratory&chapter=resp_01')
        self.page.wait_for_selector('.chapter-title')
        self.assertIn('chapter=resp_01', self.page.url)

    def test_notes_unreadable_storage_never_overwrites_and_recovers_patches(self):
        import json
        original = {'circ-valvas': {'title': 'Valvas', 'text': 'Anterior', 'extra': 1},
                    'other': {'title': 'Outra', 'text': 'Preservar'}, 'extension': {'version': 3}}
        self.context.add_init_script("""(() => {
          const get = Storage.prototype.getItem, set = Storage.prototype.setItem;
          window.noteReadsBlocked = true; window.noteWrites = 0;
          window.rawNotes = () => get.call(localStorage, 'atlas:notes:circulatory');
          set.call(localStorage, 'atlas:notes:circulatory', ORIGINAL);
          Storage.prototype.getItem = function(k) {
            if (k.startsWith('atlas:notes:') && window.noteReadsBlocked) throw new Error('blocked read');
            return get.call(this, k);
          };
          Storage.prototype.setItem = function(k, v) {
            if (k.startsWith('atlas:notes:')) window.noteWrites++;
            return set.call(this, k, v);
          };
        })();""".replace('ORIGINAL', json.dumps(json.dumps(original))))
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.locator('#study-notes').fill('Pendente')
        self.assertEqual(self.page.evaluate('window.noteWrites'), 0)
        self.assertEqual(self.page.evaluate('window.rawNotes()'), json.dumps(original))
        self.assertIn('somente nesta sessão', self.page.locator('#study-notes-status').inner_text())
        self.page.locator('#chapter-list button').first.click()
        from urllib.parse import urlparse, parse_qs
        pending_chapter = parse_qs(urlparse(self.page.url).query)['chapter'][0]
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.locator('#study-notes').fill('Segunda nota pendente')
        self.page.locator('#chapter-list button').filter(has_text='Valvas e esqueleto fibroso').click()
        self.assertEqual(self.page.locator('#study-notes').input_value(), 'Pendente')
        with self.page.expect_download() as downloaded:
            self.page.get_by_role('button', name='Baixar minhas anotações', exact=True).click()
        from pathlib import Path
        exported = Path(downloaded.value.path()).read_text(encoding='utf-8')
        self.assertIn('Pendente', exported)
        self.assertIn('Segunda nota pendente', exported)
        self.assertEqual(self.page.evaluate('window.noteWrites'), 0)
        # A second real page writes after the failed read, before recovery.
        other = self.context.new_page()
        other.goto(BASE + '/theory.html?system=respiratory')
        updated = {**original, 'other': {'title': 'Outra', 'text': 'Nova de outra aba'},
                   'circ-valvas': {**original['circ-valvas'], 'extra': 2}, 'new': {'text': 'Nova'}}
        other.evaluate('(v) => localStorage.setItem("atlas:notes:circulatory", JSON.stringify(v))', updated)
        self.page.evaluate('window.noteReadsBlocked = false')
        self.page.locator('#study-notes').fill('Pendente recuperada')
        saved = json.loads(self.page.evaluate('window.rawNotes()'))
        self.assertEqual(saved[pending_chapter]['text'], 'Segunda nota pendente')
        self.assertEqual(saved['other'], updated['other'])
        self.assertEqual(saved['new'], updated['new'])
        self.assertEqual(saved['extension'], original['extension'])
        self.assertEqual(saved['circ-valvas']['extra'], 2)
        self.assertEqual(saved['circ-valvas']['text'], 'Pendente recuperada')
        self.assertNotIn('somente nesta sessão', self.page.locator('#study-notes-status').inner_text())

    def test_notes_pending_survive_factory_system_changes_and_export_extensions(self):
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#study-notes-box', state='attached')
        self.page.evaluate("""() => {
          localStorage.setItem('atlas:notes:circulatory', JSON.stringify({extension: {version: 1}}));
          Storage.prototype.setItem = () => {throw new Error('blocked write')};
        }""")
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.locator('#study-notes').fill('Pendente circulatória')
        self.page.evaluate("""async () => {
          const {createStudyNotes} = await import('./study-notes.js');
          document.querySelector('#study-notes-box').replaceWith(
            createStudyNotes('respiratory')({id:'resp_01',title:'Respiração'}));
        }""")
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.locator('#study-notes').fill('Pendente respiratória')
        self.page.evaluate("""async () => {
          const {createStudyNotes} = await import('./study-notes.js');
          document.querySelector('#study-notes-box').replaceWith(
            createStudyNotes('circulatory')({id:'circ-valvas',title:'Valvas'}));
        }""")
        self.assertEqual(self.page.locator('#study-notes').input_value(), 'Pendente circulatória')
        self.assertIn('somente nesta sessão', self.page.locator('#study-notes-status').inner_text())
        with self.page.expect_download() as downloaded:
            self.page.get_by_role('button', name='Baixar minhas anotações', exact=True).click()
        from pathlib import Path
        self.assertIn('Pendente circulatória', Path(downloaded.value.path()).read_text(encoding='utf-8'))

    def test_notes_pending_warn_before_leaving_for_another_system(self):
        self.context.add_init_script("Storage.prototype.setItem = () => {throw new Error('blocked')}")
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.locator('#study-notes-box').evaluate('(n) => n.open = true')
        self.page.locator('#study-notes').fill('Não perder ao sair')
        dialogs = []
        def dismiss(dialog):
            dialogs.append(dialog.type)
            dialog.dismiss()
        self.page.on('dialog', dismiss)
        self.page.locator('[data-system="respiratory"]').click()
        self.assertEqual(dialogs, ['beforeunload'])
        self.assertIn('system=circulatory', self.page.url)
        self.assertEqual(self.page.locator('#study-notes').input_value(), 'Não perder ao sair')

    def test_blocked_storage_keeps_notes_in_session_and_allows_export(self):
        self.context.add_init_script("""Storage.prototype.setItem = function() { throw new DOMException('blocked', 'SecurityError'); };
          Storage.prototype.getItem = function() { throw new DOMException('blocked', 'SecurityError'); };""")
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('.chapter-title')
        self.page.locator('#study-notes-box').evaluate('(node) => node.open = true')
        self.page.get_by_label('Minhas dúvidas e explicações').fill('Dúvida local sem armazenamento')
        self.assertIn('somente nesta sessão', self.page.locator('#study-notes-status').inner_text())
        self.page.locator('#chapter-list button').first.click()
        self.page.locator('#chapter-list button').filter(has_text='Valvas e esqueleto fibroso').click()
        self.assertEqual(self.page.locator('#study-notes').input_value(), 'Dúvida local sem armazenamento')
        with self.page.expect_download() as downloaded:
            self.page.get_by_role('button', name='Baixar minhas anotações', exact=True).click()
        from pathlib import Path
        self.assertIn('Dúvida local sem armazenamento', Path(downloaded.value.path()).read_text())

if __name__ == '__main__':
    unittest.main(verbosity=2)
