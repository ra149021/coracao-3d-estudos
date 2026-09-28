"""Prepare a local-only classroom index without copying original PDFs/videos into Git."""
from pathlib import Path
import json
import fitz

ROOT=Path(__file__).resolve().parents[1]
MATERIALS=Path.home()/'Documentos/Anatomia_Circulatorio_Respiratorio_2026-09-28'
LOCAL=ROOT/'materiais/classroom'
LOCAL.mkdir(parents=True,exist_ok=True)
DOCS=[
 ('coracao','Coração','circulatory','03_Materiais_Locais/Vault_Circulacao/6. Sistema Circulatório - Coração.pdf'),
 ('vasos','Vasos sanguíneos','circulatory','03_Materiais_Locais/2 Sistema Circulatório-Vasos.pdf'),
 ('linfatico','Sistema linfático','circulatory','01_Professora_Gmail/2. Sistema Linfático.pdf'),
 ('respiratorio','Sistema respiratório','respiratory','01_Professora_Gmail/3. Sistema Respiratório Medicina.pdf'),
 ('roteiro','Roteiro prático de circulatório','circulatory','03_Materiais_Locais/Roteiro de Circulatório 3.pdf'),
 ('mediastino','Cavidade torácica e mediastino','both','05_Apoio_Torax/5. Cavidade Torácica-Mediastino.pdf'),
]
manifest={'documents':{},'videos':{},'transcripts':{}}
catalog={'version':1,'documents':[],'videos':[],'notice':'Os arquivos originais são servidos apenas na instalação local. As transcrições são automáticas e podem conter erros de termos anatômicos.'}
for id,title,system,rel in DOCS:
 path=MATERIALS/rel
 if not path.exists():continue
 doc=fitz.open(path);folder=LOCAL/id;folder.mkdir(exist_ok=True)
 for i,page in enumerate(doc):
  target=folder/f'{i+1}.jpg'
  if not target.exists():
   pix=page.get_pixmap(matrix=fitz.Matrix(1500/page.rect.width,1500/page.rect.width),alpha=False)
   pix.save(target,jpg_quality=86)
 manifest['documents'][id]={'path':str(path),'pages':len(doc),'pageDirectory':str(folder)}
 catalog['documents'].append({'id':id,'title':title,'system':system,'pages':len(doc),'kind':'Roteiro docente' if id=='roteiro' else 'Slides docentes','author':'Material de aula · Carmem / UEM'})
 print(f'{id}: {len(doc)} páginas',flush=True)
for item in json.loads((MATERIALS/'08_Videos_Obsidian/manifesto.json').read_text()):
 id=item['id'];video=Path(item['video']);base=video.parents[1];transcript=base/'Transcrições'/f'{id}.json'
 if not video.exists():video=Path(item['source'])
 if not video.exists():continue
 manifest['videos'][id]={'path':str(video)}
 if transcript.exists():
  raw=json.loads(transcript.read_text());segments=[{'start':s['start'],'end':s['end'],'text':s['text']} for s in raw.get('segments',[])]
  target=LOCAL/f'{id}-transcript.json';target.write_text(json.dumps({'id':id,'automatic':True,'segments':segments},ensure_ascii=False))
  manifest['transcripts'][id]={'path':str(target)}
 catalog['videos'].append({'id':id,'title':item['title'],'system':'respiratory' if id.startswith('R') else 'circulatory','duration':item['duration'],'automaticTranscript':transcript.exists()})
(ROOT/'materiais/library-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(ROOT/'site/assets/classroom.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
print(json.dumps({'documents':len(catalog['documents']),'videos':len(catalog['videos']),'pages':sum(d['pages'] for d in catalog['documents'])}),flush=True)
