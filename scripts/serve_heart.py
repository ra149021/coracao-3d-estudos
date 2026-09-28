"""Serve only the cardiac app on loopback. No packages or internet required."""
import argparse
import errno
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.request
import webbrowser

SITE = Path(__file__).resolve().parents[1] / 'site'

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'coracao-3d-local-v1')
            return
        path = self.path.split('?', 1)[0]
        if '..' in path or '/node_modules' in path or path.startswith('/.'):
            self.send_error(404)
            return
        return super().do_GET()

    def list_directory(self, path):
        self.send_error(404)
        return None

def main():
    args_parser = argparse.ArgumentParser(description='Coração 3D local')
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
                    if response.read(80) == b'coracao-3d-local-v1':
                        print(address, flush=True)
                        if args.open:
                            webbrowser.open(address)
                        return
            except (OSError, ValueError):
                pass
    else:
        raise SystemExit('Não foi possível abrir uma porta local entre as 20 tentativas.')
    print(f'Coração 3D: {address}\nDeixe este processo aberto. Ctrl+C encerra o servidor.', flush=True)
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
