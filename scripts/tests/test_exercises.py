"""Separate reading from the real question bank and practical destinations."""
import json
import unittest
from playwright.sync_api import sync_playwright
from test_exam_path import BASE

class ExercisesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 390, 'height': 844})
        self.context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(BASE) else r.abort())
        self.page = self.context.new_page()
    def tearDown(self):
        self.context.close()
    def test_filters_stay_disabled_and_ignore_events_during_pending_and_failed_load(self):
        errors = []
        pending = []
        self.page.on('pageerror', lambda error: errors.append(str(error)))
        self.page.route('**/assets/circulatory-theory.json', lambda route: pending.append(route))
        with self.page.expect_request('**/assets/circulatory-theory.json'):
            self.page.goto(BASE + '/exercises.html?system=respiratory&chapter=resp_09', wait_until='domcontentloaded')
        self.page.wait_for_selector('#exercise-count')
        for phase in ['pending', 'failed']:
            with self.subTest(phase=phase, behavior='disabled filters'):
                self.assertTrue(self.page.locator('#exercise-system').is_disabled())
                self.assertTrue(self.page.locator('#exercise-chapter').is_disabled())
            self.page.evaluate("""async () => {
                for (const id of ['exercise-system', 'exercise-chapter'])
                    document.getElementById(id).dispatchEvent(new Event('change'));
                await new Promise(resolve => setTimeout(resolve, 0));
            }""")
            with self.subTest(phase=phase, behavior='programmatic events are harmless'):
                self.assertEqual(errors, [])
                self.assertEqual(self.page.url, BASE + '/exercises.html?system=respiratory&chapter=resp_09')
            if phase == 'pending':
                self.assertEqual(self.page.locator('#exercise-count').inner_text(), 'Carregando perguntas…')
                self.assertEqual(len(pending), 1)
                pending[0].abort()
                self.page.get_by_role('heading', name='Exercícios indisponíveis', exact=True).wait_for()
        self.assertEqual(self.page.locator('#exercise-count').inner_text(), 'Conteúdo não carregado')
        self.assertEqual(self.page.get_by_role('button', name='Revelar resposta', exact=True).count(), 0)

    def test_successful_initialization_enables_filters_and_preserves_defaults_and_deep_links(self):
        pending = []
        errors = []
        self.page.on('pageerror', lambda error: errors.append(str(error)))
        self.page.route('**/assets/circulatory-theory.json', lambda route: pending.append(route))
        for query, system, chapter in [('', 'circulatory', ''),
                                       ('?system=respiratory&chapter=resp_09', 'respiratory', 'resp_09')]:
            with self.subTest(query=query):
                with self.page.expect_request('**/assets/circulatory-theory.json'):
                    self.page.goto(BASE + '/exercises.html' + query, wait_until='domcontentloaded')
                self.assertTrue(self.page.locator('#exercise-system').is_disabled())
                self.assertTrue(self.page.locator('#exercise-chapter').is_disabled())
                pending.pop().continue_()
                self.page.wait_for_selector('#review-body h2')
                self.assertTrue(self.page.locator('#exercise-system').is_enabled())
                self.assertTrue(self.page.locator('#exercise-chapter').is_enabled())
                self.assertEqual(self.page.locator('#exercise-system').input_value(), system)
                self.assertEqual(self.page.locator('#exercise-chapter').input_value(), chapter)
                self.assertIn('system=' + system, self.page.locator('#back-reading').get_attribute('href'))
                if chapter:
                    self.assertIn('chapter=' + chapter, self.page.url)
        self.assertEqual(errors, [])

    def test_reading_links_to_separate_filtered_training(self):
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('.chapter-title')
        self.assertEqual(self.page.locator('#review-dialog, #recall-draft').count(), 0)
        self.page.get_by_role('link', name='Praticar esta unidade', exact=True).click()
        self.page.wait_for_selector('#review-body h2')
        self.assertIn('/exercises.html?', self.page.url)
        self.assertEqual(self.page.locator('#exercise-chapter').input_value(), 'circ-valvas')
        self.assertEqual(self.page.locator('iframe').count(), 0)
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_legacy_review_redirect_preserves_system_and_unit(self):
        self.page.goto(BASE + '/theory.html?mode=review&system=respiratory&chapter=resp_09')
        self.page.wait_for_selector('#review-body h2')
        self.assertIn('/exercises.html?', self.page.url)
        self.assertEqual(self.page.locator('#exercise-system').input_value(), 'respiratory')
        self.assertEqual(self.page.locator('#exercise-chapter').input_value(), 'resp_09')

    def test_modes_keep_context_and_use_actual_practice_destination(self):
        self.page.goto(BASE + '/exercises.html?system=respiratory&chapter=resp_06')
        self.page.wait_for_selector('#review-body h2')
        self.assertIn('mode=practice', self.page.locator('#recognition-link').get_attribute('href'))
        self.assertIn('system=respiratory', self.page.locator('#recognition-link').get_attribute('href'))
        self.page.locator('#applied-link').click()
        self.page.wait_for_selector('#case-title')
        self.assertEqual(self.page.locator('#case-system').input_value(), 'respiratory')
        self.assertEqual(self.page.locator('#case-list button').count(), 1)

    def test_global_navigation_and_home_expose_distinct_reading_and_exercises(self):
        self.page.goto(BASE + '/index.html')
        self.page.wait_for_selector('.global-nav')
        self.page.get_by_role('button',name='Menu',exact=True).click()
        for label in ['Teoria', 'Exercícios']:
            self.assertEqual(self.page.locator('.global-nav').get_by_role('link', name=label, exact=True).count(), 1)
        self.assertGreater(self.page.locator('main a[href="exercises.html"]').count(), 0)

    def test_ratings_preserve_read_unknown_keys_and_notes_and_survive_reload(self):
        old={'read':{'circ-valvas':True},'answers':{'old':{'rating':'review','at':123}},'extension':{'keep':True}}
        self.context.add_init_script(f"if(!localStorage.getItem('atlas:theory:circulatory'))localStorage.setItem('atlas:theory:circulatory', {json.dumps(json.dumps(old))});")
        self.page.goto(BASE + '/exercises.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#review-body h2')
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Preciso revisar', exact=True).click()
        saved=self.page.evaluate("JSON.parse(localStorage.getItem('atlas:theory:circulatory'))")
        self.assertEqual(saved['read'], old['read'])
        self.assertEqual(saved['answers']['old'], old['answers']['old'])
        self.assertEqual(saved['extension'], old['extension'])
        self.page.reload()
        self.page.wait_for_selector('#review-body h2')
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('atlas:theory:circulatory'))"),saved)

    def test_filter_changes_and_blocked_storage_still_allow_training(self):
        self.context.add_init_script("Storage.prototype.getItem=Storage.prototype.setItem=function(){throw new Error('blocked')}")
        self.page.goto(BASE + '/exercises.html')
        self.page.wait_for_selector('#review-body h2')
        self.page.locator('#exercise-system').select_option('respiratory')
        self.page.locator('#exercise-chapter').select_option('resp_09')
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
        self.assertIn('somente nesta sessão',self.page.locator('#theory-status').inner_text())
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_unit_without_case_is_explicit_and_can_expand_to_all_cases(self):
        self.page.goto(BASE + '/exercises.html?system=respiratory&chapter=resp_09')
        self.page.wait_for_selector('#review-body h2')
        self.page.locator('#applied-link').click()
        self.page.get_by_text('Nenhum caso disponível para esta unidade.', exact=False).wait_for()
        self.assertEqual(self.page.locator('#case-list button').count(), 0)
        self.page.get_by_role('button',name='Mostrar todos os casos',exact=True).click()
        self.page.wait_for_selector('#case-title')
        self.assertEqual(self.page.locator('#case-list button').count(), 6)

    def test_write_only_storage_block_keeps_session_ratings_across_filters(self):
        self.context.add_init_script("Storage.prototype.setItem=function(){throw new Error('write blocked')}")
        self.page.goto(BASE + '/exercises.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#review-body h2')
        first=self.page.locator('#review-body h2').inner_text()
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
        self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        self.page.locator('#exercise-system').select_option('respiratory')
        self.page.locator('#exercise-system').select_option('circulatory')
        self.page.locator('#exercise-chapter').select_option('circ-valvas')
        self.assertNotEqual(self.page.locator('#review-body h2').inner_text(), first)

    def test_read_failure_preserves_original_bytes_and_session_rating(self):
        self.page.goto(BASE + '/exercises.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#review-body h2')
        first = self.page.locator('#review-body h2').inner_text()
        original = '{ "read": {"preserveMe":true}, "answers":{"other":{"rating":"known"}}, "extension":"keep" }'
        self.page.evaluate("""raw => {
            localStorage.setItem('atlas:theory:circulatory', raw);
            window.originalGet = Storage.prototype.getItem;
            Storage.prototype.getItem = function(key) {
                if (key === 'atlas:theory:circulatory') throw new Error('read blocked');
                return window.originalGet.call(this, key);
            };
        }""", original)
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
        self.assertEqual(self.page.evaluate("originalGet.call(localStorage, 'atlas:theory:circulatory')"), original)
        self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        self.page.locator('#exercise-system').select_option('respiratory')
        self.page.locator('#exercise-system').select_option('circulatory')
        self.page.locator('#exercise-chapter').select_option('circ-valvas')
        self.assertNotEqual(self.page.locator('#review-body h2').inner_text(), first)
        self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        self.assertEqual(self.page.evaluate("originalGet.call(localStorage, 'atlas:theory:circulatory')"), original)

    def check_storage_recovery(self, read_blocked, write_blocked):
        original = {'read': {'old': True}, 'answers': {'other': {'rating': 'known', 'at': 1}}, 'extension': {'old': True}}
        raw = json.dumps(original, indent=2)
        self.page.add_init_script("""(() => {
            const get = Storage.prototype.getItem, set = Storage.prototype.setItem;
            window.nativeRead = key => get.call(localStorage, key);
            window.blockRead = READ_BLOCKED;
            window.blockWrite = WRITE_BLOCKED;
            set.call(localStorage, 'atlas:theory:circulatory', SEED);
            Storage.prototype.getItem = function(key) {
                if (window.blockRead && key.startsWith('atlas:theory:')) throw new Error('read blocked');
                return get.call(this, key);
            };
            Storage.prototype.setItem = function(key, value) {
                if (window.blockWrite && key.startsWith('atlas:theory:')) throw new Error('write blocked');
                return set.call(this, key, value);
            };
        })();""".replace('READ_BLOCKED', json.dumps(read_blocked)).replace('WRITE_BLOCKED', json.dumps(write_blocked)).replace('SEED', json.dumps(raw)))
        errors = []
        self.page.on('pageerror', lambda error: errors.append(str(error)))
        self.page.goto(BASE + '/exercises.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#review-body h2')
        if read_blocked:
            self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        questions = self.page.evaluate("async () => (await (await fetch('assets/circulatory-theory.json')).json()).chapters.flatMap(c => c.recall || [])")
        ids = {q['question']: q['id'] for q in questions}
        first = self.page.locator('#review-body h2').inner_text()
        first_id = ids[first]
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
        self.assertEqual(self.page.evaluate("nativeRead('atlas:theory:circulatory')"), raw)
        self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        self.page.locator('#exercise-system').select_option('respiratory')
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Preciso revisar', exact=True).click()
        self.page.locator('#exercise-system').select_option('circulatory')
        self.page.locator('#exercise-chapter').select_option('circ-valvas')
        self.assertNotEqual(self.page.locator('#review-body h2').inner_text(), first)
        self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        # A separate real tab changes fields that are NOT part of our pending patch.
        concurrent = {'read': {'new': True}, 'answers': {'other': {'rating': 'review', 'at': 2}}, 'extension': {'new': True}, 'future': [1, 2]}
        other = self.context.new_page()
        other.goto(BASE + '/exercises.html')
        other.evaluate("value => localStorage.setItem('atlas:theory:circulatory', JSON.stringify(value))", concurrent)
        self.page.evaluate('window.blockRead = window.blockWrite = false')
        second_id = ids[self.page.locator('#review-body h2').inner_text()]
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Preciso revisar', exact=True).click()
        saved = self.page.evaluate("JSON.parse(nativeRead('atlas:theory:circulatory'))")
        for key in ['read', 'extension', 'future']:
            self.assertEqual(saved[key], concurrent[key])
        self.assertEqual(saved['answers']['other'], concurrent['answers']['other'])
        self.assertEqual(set(saved['answers']), {'other', first_id, second_id})
        self.assertEqual(saved['answers'][first_id]['rating'], 'known')
        self.assertEqual(saved['answers'][second_id]['rating'], 'review')
        self.assertIn('salva neste navegador', self.page.locator('#theory-status').inner_text())
        # A committed patch must not be replayed over a later concurrent rating.
        saved['answers'][first_id] = {'rating': 'review', 'at': 99}
        other.evaluate("value => localStorage.setItem('atlas:theory:circulatory', JSON.stringify(value))", saved)
        self.assertNotEqual(ids[self.page.locator('#review-body h2').inner_text()], first_id)
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
        self.assertEqual(self.page.evaluate("JSON.parse(nativeRead('atlas:theory:circulatory')).answers")[first_id], {'rating': 'review', 'at': 99})
        self.page.locator('#exercise-system').select_option('respiratory')
        self.assertIn('somente nesta sessão', self.page.locator('#theory-status').inner_text())
        self.assertEqual(errors, [])
        other.close()

    def test_read_only_block_recovers_pending_patch_over_concurrent_updates(self):
        self.check_storage_recovery(True, False)

    def test_write_only_block_recovers_pending_patch_over_concurrent_updates(self):
        self.check_storage_recovery(False, True)

    def test_both_storage_blocks_recover_pending_patch_over_concurrent_updates(self):
        self.check_storage_recovery(True, True)

    def test_rating_does_not_overwrite_another_tab_updated_answer(self):
        original={'read':{},'answers':{'another-question':{'rating':'known','at':10}}}
        self.context.add_init_script(f"localStorage.setItem('atlas:theory:circulatory', {json.dumps(json.dumps(original))});")
        self.page.goto(BASE + '/exercises.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#review-body h2')
        self.page.evaluate("localStorage.setItem('atlas:theory:circulatory',JSON.stringify({read:{},answers:{'another-question':{rating:'review',at:20}}}))")
        self.page.get_by_role('button', name='Revelar resposta', exact=True).click()
        self.page.get_by_role('button', name='Expliquei com segurança', exact=True).click()
        saved=self.page.evaluate("JSON.parse(localStorage.getItem('atlas:theory:circulatory'))")
        self.assertEqual(saved['answers']['another-question'],{'rating':'review','at':20})
        self.assertEqual(len(saved['answers']),2)

    def test_applied_cases_are_not_presented_as_real_patient_records(self):
        self.page.goto(BASE + '/exercises.html')
        self.page.wait_for_selector('#review-body h2')
        self.assertNotIn('casos reais', self.page.locator('#applied-link').inner_text().lower())
        self.assertIn('casos de estudo', self.page.locator('#applied-link').inner_text().lower())

    def test_corrupt_progress_does_not_disable_questions(self):
        self.context.add_init_script("localStorage.setItem('atlas:theory:circulatory', JSON.stringify('bad-shape'))")
        self.page.goto(BASE + '/exercises.html')
        self.page.get_by_role('button',name='Revelar resposta',exact=True).wait_for(timeout=5000)
        self.page.get_by_role('button',name='Revelar resposta',exact=True).click()
        self.page.get_by_role('button',name='Preciso revisar',exact=True).click()

    def test_recognition_link_opens_existing_atlas_training(self):
        self.page.goto(BASE + '/exercises.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('#review-body h2')
        self.page.locator('#recognition-link').click()
        self.page.wait_for_selector('#study-setup[open]',timeout=60000)
        self.assertEqual(self.page.locator('#study-mode option').count(), 2)

    def test_marking_read_merges_concurrent_exercise_ratings_without_erasing_extensions(self):
        self.page.goto(BASE + '/theory.html?system=circulatory&chapter=circ-valvas')
        self.page.wait_for_selector('.chapter-title')
        original={'read':{'circ-circuitos':True},'answers':{'concurrent-question':{'rating':'known','at':123}},'extension':{'keep':True}}
        self.page.evaluate('(saved)=>localStorage.setItem("atlas:theory:circulatory",JSON.stringify(saved))',original)
        self.page.get_by_role('button',name='Marcar unidade como lida',exact=True).click()
        saved=self.page.evaluate('JSON.parse(localStorage.getItem("atlas:theory:circulatory"))')
        self.assertEqual(saved['answers'],original['answers'])
        self.assertEqual(saved['extension'],original['extension'])
        self.assertTrue(saved['read']['circ-circuitos'])
        self.assertTrue(saved['read']['circ-valvas'])
