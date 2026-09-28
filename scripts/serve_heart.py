"""Serve the atlas and allowlisted teaching files on loopback."""
import argparse
import errno
import functools
import json
import mimetypes
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.request
from urllib.parse import unquote, urlsplit
import webbrowser

SITE = Path(__file__).resolve().parents[1] / 'site'
LIBRARY = SITE.parent / 'materiais/library-manifest.json'
HEALTH = b'atlas-estudo-local-v2'

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def _local(self, head=False):
        path=unquote(urlsplit(self.path).path)
        if not path.startswith('/local/'):
            return False
        try:
            manifest=json.loads(LIBRARY.read_text())
        except (OSError,ValueError):
            self.send_error(404,'Local classroom not installed')
            return True
        if path=='/local/status':
            payload=json.dumps({'documents':list(manifest['documents']),'videos':list(manifest['videos'])}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers()
            if not head:self.wfile.write(payload)
            return True
        match=re.fullmatch(r'/local/(file|page|video|transcript)/([A-Za-z0-9_-]+)(?:/(\d+))?',path)
        if not match:
            self.send_error(404);return True
        kind,id,page=match.groups();entry=manifest.get({'file':'documents','page':'documents','video':'videos','transcript':'transcripts'}[kind],{}).get(id)
        if not entry:
            self.send_error(404);return True
        if kind=='page':
            if not page or not 1<=int(page)<=entry['pages']:
                self.send_error(404);return True
            file=Path(entry['pageDirectory'])/f'{int(page)}.jpg'
        else:
            if page:
                self.send_error(404);return True
            file=Path(entry['path'])
        if not file.is_file():
            self.send_error(404);return True
        size=file.stat().st_size;start=0;end=size-1;partial=False
        if self.headers.get('Range'):
            value=re.fullmatch(r'bytes=(\d*)-(\d*)',self.headers['Range'])
            if not value or not any(value.groups()):
                self.send_error(416);return True
            first,last=value.groups()
            if first:
                start=int(first);end=min(int(last),end) if last else end
            else:start=max(0,size-int(last))
            if start>end or start>=size:
                self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return True
            partial=True
        self.send_response(206 if partial else 200)
        self.send_header('Content-Type',mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
        self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
        if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        if not head:
            try:
                with file.open('rb') as source:
                    source.seek(start);remaining=end-start+1
                    while remaining:
                        chunk=source.read(min(262144,remaining))
                        if not chunk:break
                        self.wfile.write(chunk);remaining-=len(chunk)
            except (BrokenPipeError,ConnectionResetError):pass
        return True

    def _allowed(self):
        path=unquote(urlsplit(self.path).path)
        return not any(p.startswith('.') or p=='node_modules' for p in path.split('/') if p)

    def do_HEAD(self):
        if self._local(head=True):return
        if not self._allowed():self.send_error(404);return
        return super().do_HEAD()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(HEALTH)
            return
        if self._local():return
        if not self._allowed():
            self.send_error(404)
            return
        return super().do_GET()

    def list_directory(self, path):
        self.send_error(404)
        return None

def main():
    args_parser = argparse.ArgumentParser(description='Atlas de estudo cardiorrespiratório')
    args_parser.add_argument('--port', type=int, default=8765)
    args_parser.add_argument('--open', action='store_true')
    args = args_parser.parse_args()
    # Reuse only our own existing server, never an arbitrary service on the port.
    for port in range(args.port, args.port + 20):
        address = f'http://127.0.0.1:{port}'
        try:
            server = ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Handler, directory=str(SITE)))
            break
        except OSError as error:
            if error.errno != errno.EADDRINUSE:
                raise SystemExit(f'Não foi possível iniciar o servidor local: {error}') from error
            try:
                with urllib.request.urlopen(address + '/health', timeout=0.5) as response:
                    if response.read(80) == HEALTH:
                        print(address, flush=True)
                        if args.open:
                            webbrowser.open(address)
                        return
            except (OSError, ValueError):
                pass
    else:
        raise SystemExit('Não foi possível abrir uma porta local entre as 20 tentativas.')
    print(f'Atlas de estudo: {address}\nDeixe este processo aberto. Ctrl+C encerra o servidor.', flush=True)
    if args.open:
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
