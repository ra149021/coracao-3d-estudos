"""Read-only structural checks for teaching data and the curated path."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILES = {'circulatory': 'site/assets/circulatory-theory.json', 'respiratory': 'site/assets/respiratory/theory.json'}

class StudyContentTests(unittest.TestCase):
    def test_ids_and_original_section_positions_are_preserved(self):
        for name in FILES.values():
            current = json.loads((ROOT / name).read_text())
            original = json.loads(subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT))
            self.assertEqual([c['id'] for c in original['chapters']], [c['id'] for c in current['chapters']])
            self.assertEqual(original['sources'], current['sources'][:len(original['sources'])])
            for old, new in zip(original['chapters'], current['chapters']):
                for i, section in enumerate(old['sections']):
                    updated = new['sections'][i]
                    self.assertEqual(section['heading'], updated['heading'])
                    for field in ['paragraphs', 'bullets', 'references']:
                        if field in section:
                            self.assertEqual(section[field], updated[field][:len(section[field])])
                    if 'table' in section:
                        self.assertEqual(section['table'], updated['table'])
                self.assertEqual(old['recall'], new['recall'][:len(old['recall'])])

    def test_questions_have_unique_ids_answers_and_resolvable_sources(self):
        for name in FILES.values():
            data = json.loads((ROOT / name).read_text())
            sources = {source['id']: source for source in data['sources']}
            questions = [q for chapter in data['chapters'] for q in chapter['recall']]
            self.assertEqual(len(questions), len({q['id'] for q in questions}))
            for question in questions:
                for field in ['question', 'answer', 'explanation']:
                    self.assertTrue(question.get(field, '').strip(), (question['id'], field))
                self.assertTrue(question.get('references'), question['id'])
            for chapter in data['chapters']:
                for section in chapter['sections'] + chapter['recall']:
                    for ref in section.get('references', []):
                        source = sources.get(ref['source'])
                        self.assertIsNotNone(source, ref)
                        assert source is not None
                        if isinstance(ref.get('page'), int) and source.get('pageCount'):
                            self.assertTrue(1 <= ref['page'] <= source['pageCount'], ref)

    def test_all_path_links_and_question_ids_resolve(self):
        data = {system: json.loads((ROOT / name).read_text()) for system, name in FILES.items()}
        guide = json.loads((ROOT / 'site/assets/exam-path.json').read_text())
        self.assertEqual(len(guide['topics']), len({topic['id'] for topic in guide['topics']}))
        for topic in guide['topics']:
            self.assertTrue(topic['flow'] and topic['targets'] and topic['questions'])
            for system, chapter_id in topic['chapters']:
                self.assertIn(chapter_id, {c['id'] for c in data[system]['chapters']})
            for system, question_id in topic['questions']:
                self.assertIn(question_id, {q['id'] for c in data[system]['chapters'] for q in c['recall']})

if __name__ == '__main__':
    unittest.main(verbosity=2)
