"""Supplement integration preserves real content and is byte-idempotent."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('supplement', ROOT / 'scripts/integrate_study_supplement.py')
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class SupplementIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.root = Path(self.tmp.name)
        self.before = {}
        for name in [*module.FILES.values(), 'site/assets/expanded-study-supplement.json']:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
            if name in module.FILES.values():
                data = json.loads(path.read_text())
                for chapter in data['chapters']:
                    chapter['sections'] = [s for s in chapter['sections'] if not s.get('id', '').startswith('expanded-section-')]
                    chapter.pop('appliedCases', None)
                path.write_text(json.dumps(data, ensure_ascii=False))
                self.before[name] = copy.deepcopy(data)

    def tearDown(self):
        self.tmp.cleanup()

    def test_integrates_without_changing_existing_questions_or_sections(self):
        changed = module.integrate(self.root)
        self.assertIn('site/assets/study-cases.json', changed)
        for name, old in self.before.items():
            new = json.loads((self.root / name).read_text())
            for before, after in zip(old['chapters'], new['chapters']):
                self.assertEqual(before['id'], after['id'])
                self.assertEqual(before['recall'], after['recall'])
                self.assertEqual(before['sections'], after['sections'][:len(before['sections'])])
        cases = json.loads((self.root / 'site/assets/study-cases.json').read_text())['cases']
        self.assertEqual(len(cases), 6)
        self.assertEqual(sum(len(c.get('appliedCases', [])) for name in module.FILES.values() for c in json.loads((self.root / name).read_text())['chapters']), len(cases))

    def test_repeated_integration_is_byte_identical_and_check_is_read_only(self):
        module.integrate(self.root)
        paths = [self.root / name for name in [*module.FILES.values(), 'site/assets/study-cases.json']]
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(module.integrate(self.root), [])
        self.assertEqual(module.integrate(self.root, check=True), [])
        self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})

    def test_unknown_source_fails_before_writing_teaching_data(self):
        path = self.root / 'site/assets/expanded-study-supplement.json'
        data = json.loads(path.read_text())
        data['cases'][0]['references'] = [{'source': 'unreviewed-source'}]
        path.write_text(json.dumps(data))
        before = {name: (self.root / name).read_bytes() for name in module.FILES.values()}
        with self.assertRaisesRegex(ValueError, 'No reviewed public source mapping'):
            module.integrate(self.root)
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        self.assertFalse((self.root / 'site/assets/study-cases.json').exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)
