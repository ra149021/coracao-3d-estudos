"""Prepare web copies after authorization; originals remain untouched and outside Git."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'materiais/public-video'
OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'materiais/library-manifest.json').read_text())

def prepare(item):
    identifier,entry=item
    source=Path(entry['path'])
    target=OUT/f'{identifier}.mp4'
    if not target.exists():
        temporary=OUT/f'{identifier}.partial.mp4'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(source),
            '-map','0:v:0','-map','0:a:0','-vf','fps=12','-c:v','libopenh264',
            '-b:v','650k','-maxrate','900k','-bufsize','1800k','-g','24','-threads','2',
            '-c:a','aac','-b:a','64k','-movflags','+faststart','-map_metadata','-1',
            '-y',str(temporary)],check=True)
        temporary.replace(target)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
        '-show_format','-of','json',str(target)]))
    duration=float(probe['format']['duration'])
    row={'id':identifier,'file':target.name,'sourceBytes':source.stat().st_size,
         'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
         'duration':duration,'streams':[{k:s.get(k) for k in
             ['codec_type','codec_name','width','height','r_frame_rate']} for s in probe['streams']]}
    print(json.dumps(row,ensure_ascii=False),flush=True)
    return row

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results=list(executor.map(prepare,manifest['videos'].items()))
(OUT/'manifest.json').write_text(json.dumps({'videos':results},ensure_ascii=False,indent=2))
