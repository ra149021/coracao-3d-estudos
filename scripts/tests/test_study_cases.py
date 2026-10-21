"""Validação estrutural CLI; não substitui auditoria anatômica humana."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
THEORIES = {
    'circulatory': 'site/assets/circulatory-theory.json',
    'respiratory': 'site/assets/respiratory/theory.json',
}


class StudyCasesTest(unittest.TestCase):
    def test_cases_contract_and_references(self):
        path = ROOT / 'site/assets/study-cases.json'
        self.assertTrue(path.is_file(), 'study-cases.json ainda não existe')
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(set(data), {'version', 'notice', 'cases'})
        self.assertEqual(type(data['version']), int)
        self.assertEqual(data['version'], 1)
        self.assertTrue(isinstance(data['notice'], str) and data['notice'].strip())
        self.assertIsInstance(data['cases'], list)
        self.assertTrue(6 <= len(data['cases']) <= 8)
        theories = {k: json.loads((ROOT / v).read_text(encoding='utf-8')) for k, v in THEORIES.items()}
        docs = {d['id']: d for d in json.loads((ROOT / 'site/assets/public-documents.json').read_text())['documents']}
        existing_questions = {q['question'].strip().casefold() for t in theories.values() for c in t['chapters'] for q in c['recall']}
        existing_ids = {obj['id'] for t in theories.values() for c in t['chapters'] for obj in [c, *c['recall']]}
        seen_ids, seen_questions = set(), set()
        required = {'id', 'title', 'system', 'chapterId', 'scenario', 'question', 'answer', 'explanation', 'checkpoints', 'references'}
        for case in data['cases']:
            with self.subTest(case=case.get('id')):
                self.assertTrue(required <= set(case) <= required | {'figure'})
                for key in required - {'checkpoints', 'references'}:
                    self.assertTrue(isinstance(case[key], str) and case[key].strip(), key)
                    self.assertNotIn('/home/', case[key])
                    self.assertNotIn('file://', case[key])
                self.assertNotIn(case['id'], seen_ids | existing_ids)
                seen_ids.add(case['id'])
                question = case['question'].strip().casefold()
                self.assertNotIn(question, existing_questions | seen_questions)
                seen_questions.add(question)
                self.assertIn(case['system'], theories)
                theory = theories[case['system']]
                self.assertIn(case['chapterId'], {c['id'] for c in theory['chapters']})
                self.assertIsInstance(case['checkpoints'], list)
                self.assertTrue(2 <= len(case['checkpoints']) <= 3)
                self.assertEqual(len(set(case['checkpoints'])), len(case['checkpoints']))
                self.assertTrue(all(isinstance(s, str) and s.strip() for s in case['checkpoints']))
                self.assertIsInstance(case['references'], list)
                self.assertTrue(case['references'])
                sources = {s['id']: s for s in theory['sources']}
                for ref in case['references']:
                    self.assertTrue({'source'} <= set(ref) <= {'source', 'page'})
                    self.assertIn(ref['source'], sources)
                    if 'page' in ref:
                        self.assertIs(type(ref['page']), int)
                        self.assertGreater(ref['page'], 0)
                        self.assertLessEqual(ref['page'], sources[ref['source']].get('pageCount', ref['page']))
                if 'figure' in case:
                    figure = case['figure']
                    self.assertEqual(set(figure), {'source', 'page'})
                    self.assertIn(figure, case['references'])
                    self.assertIn(figure['source'], docs)
                    doc = docs[figure['source']]
                    self.assertIs(type(figure['page']), int)
                    self.assertTrue(1 <= figure['page'] <= doc['pages'])
                    self.assertTrue((ROOT / 'site' / doc['pageBaseUrl'] / (str(figure['page']) + '.jpg')).is_file())

    def test_theory_question_ids_and_all_reference_targets(self):
        for system, filename in THEORIES.items():
            theory = json.loads((ROOT / filename).read_text(encoding='utf-8'))
            ids = []
            sources = {s['id']: s for s in theory['sources']}
            self.assertEqual(len(sources), len(theory['sources']))
            for chapter in theory['chapters']:
                ids.append(chapter['id'])
                for question in chapter['recall']:
                    ids.append(question['id'])
                    for key in ('question', 'answer', 'explanation'):
                        self.assertTrue(question[key].strip())
            self.assertEqual(len(ids), len(set(ids)), system)
            def walk(value):
                if isinstance(value, dict):
                    if 'source' in value:
                        self.assertIn(value['source'], sources)
                        if 'page' in value:
                            self.assertIs(type(value['page']), int)
                            self.assertGreater(value['page'], 0)
                            self.assertLessEqual(value['page'], sources[value['source']].get('pageCount', value['page']))
                    for child in value.values():
                        walk(child)
                elif isinstance(value, list):
                    for child in value:
                        walk(child)
            walk(theory)


if __name__ == '__main__':
    unittest.main(verbosity=2)
