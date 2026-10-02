"""Check authored theory against the local teaching pages and anatomy indexes."""
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / 'site'


def read(relative):
    return json.loads((SITE / relative).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    totals = {'chapters': 0, 'sections': 0, 'sectionsWithFigures': 0,
              'figureAssociations': 0, 'textQuestions': 0, 'visualQuestions': 0}
    question_ids = set()
    for system, theory_path, catalog_path, route_path in [
        ('circulatory', 'assets/circulatory-theory.json', 'assets/catalog.json', 'auditoria/matriz_coracao.json'),
        ('respiratory', 'assets/respiratory/theory.json', 'assets/respiratory/catalog.json', 'assets/respiratory/requirements.json'),
    ]:
        theory = read(theory_path)
        sources = {source['id']: source for source in theory['sources']}
        parts = {part['id'] for part in read(catalog_path)['parts']}
        targets = {str(target['id']) for target in read(route_path)['alvos']}
        chapter_ids = set()

        def check_figure(figure, context):
            source, page = figure.get('source'), figure.get('page')
            require(source in sources, f'{context}: unknown source {source}')
            require(type(page) is int and page > 0, f'{context}: invalid page {page}')
            require(page <= sources[source].get('pageCount', 0), f'{context}: page outside source {page}')
            require((SITE / 'assets/lectures/slides' / source / f'{page}.jpg').is_file(),
                    f'{context}: missing teaching page {source}/{page}.jpg')

        for chapter in theory['chapters']:
            chapter_id = chapter['id']
            require(chapter_id not in chapter_ids, f'{system}: duplicate chapter {chapter_id}')
            chapter_ids.add(chapter_id)
            totals['chapters'] += 1
            require(set(chapter.get('partIds', [])) <= parts, f'{chapter_id}: unknown anatomy part')
            require(set(map(str, chapter.get('requirementIds', []))) <= targets,
                    f'{chapter_id}: unknown route target')
            for section in chapter['sections']:
                totals['sections'] += 1
                figures = section.get('figures', [])
                totals['sectionsWithFigures'] += bool(figures)
                for figure in figures:
                    check_figure(figure, chapter_id)
                    require(any(reference.get('source') == figure['source'] and reference.get('page') == figure['page']
                                for reference in section.get('references', []) if isinstance(reference, dict)),
                            f'{chapter_id}: figure is not a reference of its section')
                    totals['figureAssociations'] += 1
            for field, counter in [('recall', 'textQuestions'), ('visualRecall', 'visualQuestions')]:
                for question in chapter.get(field, []):
                    question_id = question['id']
                    require(question_id not in question_ids, f'Duplicate question ID {question_id}')
                    question_ids.add(question_id)
                    require(question.get('question') and question.get('answer'), f'{question_id}: missing question or answer')
                    if field == 'visualRecall':
                        require(question.get('figures'), f'{question_id}: visual task without a figure')
                        for figure in question['figures']:
                            check_figure(figure, question_id)
                            require(any(reference.get('source') == figure['source'] and reference.get('page') == figure['page']
                                        for reference in question.get('references', []) if isinstance(reference, dict)),
                                    f'{question_id}: figure lacks a question reference')
                    totals[counter] += 1
    print(json.dumps({'status': 'ok', **totals}, ensure_ascii=False))


if __name__ == '__main__':
    main()
