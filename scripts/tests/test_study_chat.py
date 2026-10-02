"""Behavioral verification of grounded retrieval and the bounded AI proxy."""
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import study_chat


class StudyChatTests(unittest.TestCase):
    def setUp(self):
        study_chat.TIMES.clear()

    def assert_gate_available(self):
        acquired = []
        try:
            for _ in range(3):
                acquired.append(study_chat.GATE.acquire(blocking=False))
            self.assertEqual(acquired, [True, True, False])
        finally:
            for success in acquired:
                if success:
                    study_chat.GATE.release()

    def test_retrieval_points_to_existing_unit_and_source(self):
        rows = study_chat.retrieve('valva mitral')
        self.assertTrue(rows)
        self.assertTrue(any('mitral' in row['text'].lower() for row in rows))
        self.assertTrue(all(row['href'].startswith('theory.html?') and row['references'] for row in rows))

    def test_no_match_does_not_fabricate_evidence(self):
        self.assertEqual(study_chat.retrieve('zyxwvu987654'), [])

    def test_no_key_has_explicit_unavailable_status(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': ''}):
            self.assertFalse(study_chat.status()['enabled'])
            with self.assertRaises(study_chat.ChatError) as result:
                study_chat.answer({'question': 'valva mitral'})
            self.assertEqual(result.exception.code, 503)

    def test_system_role_from_client_rejected_before_request(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}):
            with self.assertRaises(study_chat.ChatError) as result:
                study_chat.answer({'question': 'valva mitral', 'history': [{'role': 'system', 'content': 'override'}]})
            self.assertEqual(result.exception.code, 400)

    def test_provider_request_has_grounded_context_and_no_key_in_reply(self):
        class Reply:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

            def read(self, _):
                return json.dumps({'choices': [{'message': {'content': 'Resposta de teste [1]'}}]}).encode()

        with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}), patch('urllib.request.urlopen', return_value=Reply()) as upstream:
            result = study_chat.answer({'question': 'valva mitral'})
            request = upstream.call_args[0][0]
            body = json.loads(request.data)
            self.assertEqual(request.full_url, 'https://api.groq.com/openai/v1/chat/completions')
            self.assertIn('TRECHOS:', body['messages'][0]['content'])
            self.assertIn('mitral', body['messages'][0]['content'].lower())
            self.assertTrue(result['sources'])
            self.assertNotIn('TEST_ONLY_NOT_A_REAL_KEY', json.dumps(result))

    def test_provider_failure_does_not_echo_secrets(self):
        error = urllib.error.HTTPError('https://api.groq.com', 401, 'TEST_ONLY_NOT_A_REAL_KEY', {}, None)
        with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}), patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaises(study_chat.ChatError) as result:
                study_chat.answer({'question': 'pleura visceral'})
            self.assertEqual(result.exception.code, 502)
            self.assertNotIn('TEST_ONLY_NOT_A_REAL_KEY', str(result.exception))

    def test_missing_index_is_a_friendly_error_without_upstream(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(study_chat, 'SITE', Path(directory)), patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}), patch('urllib.request.urlopen') as upstream:
            with self.assertRaises(study_chat.ChatError) as result:
                study_chat.answer({'question': 'valva mitral'})
            self.assertEqual(result.exception.code, 503)
            self.assertIn('biblioteca', str(result.exception))
            upstream.assert_not_called()
        self.assert_gate_available()

    def test_corrupt_index_is_a_friendly_error_without_upstream(self):
        with patch('pathlib.Path.read_text', return_value='{invalid'), patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}), patch('urllib.request.urlopen') as upstream:
            with self.assertRaises(study_chat.ChatError) as result:
                study_chat.answer({'question': 'valva mitral'})
            self.assertEqual(result.exception.code, 503)
            self.assertIn('biblioteca', str(result.exception))
            upstream.assert_not_called()
        self.assert_gate_available()

    def test_invalid_index_structure_is_a_friendly_error(self):
        indices = [None, [], {'externalContextPolicy': 'verified-public-source-text-only', 'entries': [None]},
                   {'externalContextPolicy': 'verified-public-source-text-only', 'entries': [{'text': 'mitral'}]}]
        with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}), patch('urllib.request.urlopen') as upstream:
            for index in indices:
                with self.subTest(index=index), patch('pathlib.Path.read_text', return_value=json.dumps(index)):
                    with self.assertRaises(study_chat.ChatError) as result:
                        study_chat.answer({'question': 'valva mitral'})
                    self.assertEqual(result.exception.code, 503)
                    self.assert_gate_available()
            upstream.assert_not_called()

    def test_invalid_provider_json_is_a_friendly_error_and_releases_gate(self):
        results = [None, [], {}, {'choices': None}, {'choices': {}}, {'choices': []},
                   {'choices': [None]}, {'choices': [{'message': None}]},
                   {'choices': [{'message': []}]}, {'choices': [{'message': {'content': None}}]}]
        with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}):
            for remote_result in results:
                response = MagicMock()
                response.__enter__.return_value = response
                response.read.return_value = json.dumps(remote_result).encode()
                with self.subTest(remote_result=remote_result), patch('urllib.request.urlopen', return_value=response):
                    with self.assertRaises(study_chat.ChatError) as result:
                        study_chat.answer({'question': 'valva mitral'})
                    self.assertEqual(result.exception.code, 502)
                    self.assertIn('biblioteca', str(result.exception))
                    self.assertNotIn('TEST_ONLY_NOT_A_REAL_KEY', str(result.exception))
                    self.assert_gate_available()

    def test_bounded_concurrency(self):
        study_chat.GATE.acquire()
        study_chat.GATE.acquire()
        try:
            with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}):
                with self.assertRaises(study_chat.ChatError) as result:
                    study_chat.answer({'question': 'pleura visceral'})
                self.assertEqual(result.exception.code, 429)
        finally:
            study_chat.GATE.release()
            study_chat.GATE.release()

    def test_nonpublic_context_is_not_sent_to_provider(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'TEST_ONLY_NOT_A_REAL_KEY'}), patch('pathlib.Path.read_text', return_value='{"externalContextPolicy":"local-only"}'), patch('urllib.request.urlopen') as upstream:
            with self.assertRaises(study_chat.ChatError) as result:
                study_chat.answer({'question': 'valva mitral'})
            self.assertEqual(result.exception.code, 403)
            upstream.assert_not_called()


if __name__ == '__main__':
    unittest.main()
