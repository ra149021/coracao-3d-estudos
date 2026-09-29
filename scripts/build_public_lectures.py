"""Index only explicitly uploaded lecture IDs and publish their automatic search transcripts."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--ids',nargs='+',required=True)
parser.add_argument('--release',default='aulas-v1')
args=parser.parse_args()
local=json.loads((ROOT/'materiais/library-manifest.json').read_text())
catalog=json.loads((ROOT/'site/assets/classroom.json').read_text())
out=ROOT/'site/assets/lectures/transcripts'
out.mkdir(parents=True,exist_ok=True)
videos=[]
for identifier in args.ids:
    item=next(v for v in catalog['videos'] if v['id']==identifier)
    path=ROOT/'materiais/public-video'/f'{identifier}.mp4'
    assert path.is_file(),identifier
    transcript=json.loads(Path(local['transcripts'][identifier]['path']).read_text())
    sanitized={'id':identifier,'automatic':True,'notice':'Transcrição automática, não revisada integralmente. Confira os termos anatômicos no áudio e nas referências.',
        'segments':[{'start':s['start'],'end':s['end'],'text':s['text']} for s in transcript['segments']]}
    (out/f'{identifier}.json').write_text(json.dumps(sanitized,ensure_ascii=False,separators=(',',':')))
    videos.append({'id':identifier,'title':item['title'],'duration':item['duration'],
        'url':f'https://github.com/ra149021/coracao-3d-estudos/releases/download/{args.release}/{identifier}.mp4',
        'transcriptUrl':f'assets/lectures/transcripts/{identifier}.json',
        'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'resolution':'1920×1080','format':'H.264 / AAC','fps':12})
index={'version':1,'author':'Material docente · Carmem / UEM','videos':videos,
    'notice':'Cópias web das videoaulas. Publicação autorizada pelo usuário, que confirmou autorização docente. O material tem autoria própria e não integra as licenças das malhas ou figuras do atlas.'}
(ROOT/'site/assets/public-lectures.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'videos':len(videos),'bytes':sum(v['bytes'] for v in videos)}))
