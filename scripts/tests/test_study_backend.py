"""Backend contract tests; all mutated libraries live beneath TMPDIR."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]


class StudyBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'])
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'site'
        self.write('theory.html', '<html></html>')
        for system, name in [('circulatory', 'circulatory-theory.json'), ('respiratory', 'respiratory/theory.json')]:
            self.write('assets/' + name, {
                'version': 1, 'system': system,
                'sources': [{'id': 'slides', 'pageCount': 1}],
                'chapters': [{'id': system + '-one', 'title': 'Título <b>real</b>',
                              'summary': 'Resumo', 'objectives': ['Objetivo'],
                              'sections': [{'heading': 'Seção', 'paragraphs': ['Mecanismo cardíaco'],
                                            'references': [{'source': 'slides', 'page': 1}],
                                            'table': {'headers': ['Coluna'], 'rows': [['Célula']]}}],
                              'recall': [{'id': system + '-q1', 'question': 'Pergunta?',
                                          'answer': 'Resposta', 'explanation': 'Explicação'}]}]})

    def write(self, name, data):
        path = self.site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data, encoding='utf-8')
        return path

    def complete_library(self):
        self.write('assets/public-documents.json', {'documents': [{'id': 'slides', 'pages': 1, 'pageBaseUrl': 'assets/slides', 'pdfUrl': 'https://example.test/slides.pdf'}]})
        image = self.site / 'assets/slides/1.jpg'
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b'\xff\xd8\xfffixture\xff\xd9')
        videos = []
        for ident in ['C1', 'C2', 'C3', 'R1', 'R2', 'R3', 'R4']:
            url = 'assets/lectures/transcripts/' + ident + '.json'
            videos.append({'id': ident, 'duration': 10, 'transcriptUrl': url, 'url': 'https://example.test/' + ident + '.mp4'})
            self.write(url, {'id': ident, 'automatic': True, 'notice': 'ASR não revisada', 'segments': [{'start': 0, 'end': 9, 'text': 'Texto real'}]})
        self.write('assets/public-lectures.json', {'videos': videos})
        self.write('assets/catalog.json', {'parts': []})
        self.write('assets/respiratory/catalog.json', {'parts': []})
        self.write('assets/respiratory/requirements.json', {'alvos': []})
        self.assertEqual(self.run_cli('build_study_search.py').returncode, 0)

    def test_validate_complete_library_marks_external_as_untested(self):
        self.complete_library()
        result = self.run_cli('validate_study_library.py', '--json')
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['counts']['transcripts'], 7)
        self.assertEqual(report['counts']['jpgPages'], 1)
        self.assertIn('https://example.test/slides.pdf', report['externalNotTested'])

    def test_build_rejects_invalid_source_without_overwriting_index(self):
        self.complete_library()
        index = self.site / 'assets/search-index.json'
        before = index.read_bytes()
        source = self.site / 'assets/circulatory-theory.json'
        original = source.read_bytes()
        for mutation in ['duplicate', 'bad id', 'wrong system', 'malformed']:
            with self.subTest(mutation=mutation):
                data = json.loads(original)
                if mutation == 'duplicate':
                    data['chapters'].append(data['chapters'][0])
                elif mutation == 'bad id':
                    data['chapters'][0]['id'] = '../private'
                elif mutation == 'wrong system':
                    data['system'] = 'private'
                self.write('assets/circulatory-theory.json', '{' if mutation == 'malformed' else data)
                result = self.run_cli('build_study_search.py')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ERROR:', result.stderr)
                self.assertEqual(index.read_bytes(), before)
        source.write_bytes(original)

    def test_build_check_detects_staleness_without_writing(self):
        self.complete_library()
        index = self.site / 'assets/search-index.json'
        before = index.read_bytes()
        self.assertEqual(self.run_cli('build_study_search.py', '--check').returncode, 0)
        source = self.site / 'assets/circulatory-theory.json'
        source.write_text(source.read_text() + '\n', encoding='utf-8')
        result = self.run_cli('build_study_search.py', '--check')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('stale', result.stderr)
        self.assertEqual(index.read_bytes(), before)

    def test_index_excludes_source_metadata_html_and_private_paths(self):
        source = self.site / 'assets/circulatory-theory.json'
        data = json.loads(source.read_text())
        data['sources'][0]['privatePath'] = '/home/private/material.pdf'
        data['chapters'][0]['sections'][0]['paragraphs'] = ['<script>secret()</script><p>Texto &amp; anatomia</p>']
        self.write('assets/circulatory-theory.json', data)
        result = self.run_cli('build_study_search.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.site / 'assets/search-index.json').read_text()
        self.assertIn('Texto & anatomia', text)
        self.assertNotIn('secret()', text)
        self.assertNotIn('/home/private', text)
        self.assertNotIn('<script>', text)

    def test_build_rejects_source_symlink_outside_public_site(self):
        source = self.site / 'assets/circulatory-theory.json'
        private = self.root / 'private.json'
        private.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(private)
        result = self.run_cli('build_study_search.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('outside', result.stderr)

    def test_validation_rejects_corrupted_public_library(self):
        self.complete_library()
        cases = [
            ('stale', 'assets/search-index.json', lambda d: d['sourceHashes'].clear(), 'stale'),
            ('index text', 'assets/search-index.json', lambda d: d['items'][0].update(text='fake'), 'stale'),
            ('duplicate', 'assets/circulatory-theory.json', lambda d: d['chapters'].append(d['chapters'][0]), 'duplicate'),
            ('unknown source', 'assets/circulatory-theory.json', lambda d: d['chapters'][0]['sections'][0]['references'][0].update(source='missing'), 'source'),
            ('invalid page', 'assets/circulatory-theory.json', lambda d: d['chapters'][0]['sections'][0]['references'][0].update(page=2), 'page'),
            ('missing part', 'assets/circulatory-theory.json', lambda d: d['chapters'][0].update(partIds=['missing']), 'part'),
            ('missing requirement', 'assets/respiratory/theory.json', lambda d: d['chapters'][0].update(requirementIds=['missing']), 'requirement'),
            ('bad chapter id', 'assets/respiratory/theory.json', lambda d: d['chapters'][0].update(id='../private'), 'id'),
            ('transcript empty', 'assets/lectures/transcripts/C1.json', lambda d: d.update(segments=[]), 'segments'),
            ('transcript time', 'assets/lectures/transcripts/C1.json', lambda d: d['segments'][0].update(end=-1), 'time'),
            ('transcript id', 'assets/lectures/transcripts/C1.json', lambda d: d.update(id='wrong'), 'transcript'),
            ('missing lecture', 'assets/public-lectures.json', lambda d: d['videos'].pop(), 'seven'),
            ('unsafe path', 'assets/public-documents.json', lambda d: d['documents'][0].update(pageBaseUrl='../private'), 'outside'),
        ]
        for label, name, mutate, message in cases:
            with self.subTest(label=label):
                path = self.site / name
                before = path.read_bytes()
                data = json.loads(before)
                mutate(data)
                self.write(name, data)
                result = self.run_cli('validate_study_library.py', '--json')
                path.write_bytes(before)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(message, ' '.join(json.loads(result.stdout)['errors']).lower())

    def test_validation_rejects_missing_jpg_and_new_static_assets(self):
        self.complete_library()
        (self.site / 'assets/slides/1.jpg').unlink()
        self.write('search.html', '<link href="new.css" rel="stylesheet"><a href="theory.html?system=circulatory&chapter=absent">Bad</a><script src="new.js"></script>')
        result = self.run_cli('validate_study_library.py', '--json')
        self.assertNotEqual(result.returncode, 0)
        errors = ' '.join(json.loads(result.stdout)['errors'])
        for term in ['1.jpg', 'new.css', 'new.js', 'absent']:
            self.assertIn(term, errors)

    def test_validation_rejects_bad_css_js_and_fragment_links(self):
        self.complete_library()
        self.write('new.css', 'main{background:url("missing.svg")}')
        self.write('new.js', 'import "./missing.js"; fetch("assets/missing.json");')
        self.write('search.html', '<a href="theory.html#nonexistent">Broken anchor</a>')
        result = self.run_cli('validate_study_library.py', '--json')
        self.assertNotEqual(result.returncode, 0)
        errors = ' '.join(json.loads(result.stdout)['errors'])
        for term in ['missing.svg', 'missing.js', 'missing.json', 'nonexistent']:
            self.assertIn(term, errors)

    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(REPO / 'scripts' / script), '--root', str(self.root), *args],
                              capture_output=True, text=True)

    def test_build_real_chapter_text_and_is_byte_idempotent(self):
        result = self.run_cli('build_study_search.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.site / 'assets/search-index.json'
        first = path.read_bytes()
        index = json.loads(first)
        self.assertEqual(index['version'], 1)
        self.assertEqual(len(index['items']), 2)
        item = index['items'][0]
        self.assertEqual(set(item), {'id', 'system', 'chapterId', 'title', 'summary', 'text', 'url'})
        for term in ['Mecanismo cardíaco', 'Célula', 'Pergunta?', 'Resposta', 'Explicação']:
            self.assertIn(term, item['text'])
        self.assertNotIn('<b>', item['title'])
        self.assertEqual(item['url'], 'theory.html?system=circulatory&chapter=circulatory-one')
        self.assertEqual(set(index['sourceHashes']), {'assets/circulatory-theory.json', 'assets/respiratory/theory.json'})
        self.assertEqual(self.run_cli('build_study_search.py').returncode, 0)
        self.assertEqual(first, path.read_bytes())


if __name__ == '__main__':
    unittest.main()
