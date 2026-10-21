"""Standalone HRA QA. Run with atlas-qa-venv Python; no shared tests edited."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import struct
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'site/assets/coronary-hra'

class CoronaryReference(unittest.TestCase):
    def test_integrity(self):
        m = json.loads((ASSETS / 'manifest.json').read_text())
        self.assertEqual(len(m['parts']), 17)
        self.assertEqual(sum(p['group'] == 'arteries' for p in m['parts']), 9)
        self.assertEqual(sum(p['group'] == 'veins' for p in m['parts']), 8)
        self.assertNotIn('/home/', json.dumps(m))
        for s in m['sources']:
            b = (ASSETS / s['file']).read_bytes()
            self.assertEqual(len(b), s['bytes'])
            self.assertEqual(hashlib.sha256(b).hexdigest(), s['sha256'])
            self.assertEqual(b[:4], b'glTF')
            g = json.loads(b[20:20 + struct.unpack_from('<I', b, 12)[0]])
            names = [n['name'] for n in g['nodes'] if 'mesh' in n]
            self.assertEqual(names, s['mesh_names'])
            if s['role'] == 'vessels':
                self.assertTrue(all(p['name'] in names for p in m['parts']))
            else:
                self.assertEqual(len(names), 14)
            self.assertEqual(s['license'], 'CC BY 4.0')
            self.assertTrue(s['datacite_evidence']['license'])

    def test_browser(self):
        from playwright.sync_api import sync_playwright
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'site')))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/coronary-reference.html'
        evidence = Path(os.environ.get('CORONARY_QA_DIR', str(Path.home() / '.hermes/cache/scratch/coronary-hra-qa')))
        evidence.mkdir(parents=True, exist_ok=True)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
                page = browser.new_page(viewport={'width': 1400, 'height': 1100})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('console', lambda e: errors.append(e.text) if e.type == 'error' else None)
                page.goto(url)
                page.wait_for_function('window.coronaryReference?.snapshot().ready', timeout=120000)
                snap = lambda: page.evaluate('window.coronaryReference.snapshot()')
                initial = snap()
                self.assertEqual(initial['visibleMeshes'], 31)
                self.assertGreater(initial['drawCalls'], 0)
                self.assertGreater(initial['triangles'], 0)
                self.assertTrue(all(m['opacity'] == 1 for m in initial['meshes']))
                page.locator('#viewport').screenshot(path=str(evidence / 'view-a.png'))
                page.click('#view-b')
                self.assertNotEqual(initial['camera'], snap()['camera'])
                page.locator('#viewport').screenshot(path=str(evidence / 'view-b.png'))
                names = page.locator('#parts button').evaluate_all('(bs)=>bs.map(b=>b.dataset.name)')
                self.assertEqual(len(names), 17)
                for name in names:
                    page.locator(f'button[data-name="{name}"]').click()
                    self.assertEqual(snap()['selected'], name)
                    self.assertEqual(snap()['visibleMeshes'], 31)
                    page.click('#isolate')
                    self.assertEqual(snap()['visibleMeshes'], 1)
                    self.assertGreater(snap()['drawCalls'], 0)
                    page.click('#isolate')
                page.click('#reset')
                page.select_option('#wall', 'translucent')
                self.assertEqual(sum(m['opacity'] < 1 for m in snap()['meshes']), 14)
                page.select_option('#wall', 'vessels')
                self.assertEqual(snap()['visibleMeshes'], 17)
                page.uncheck('#arteries'); self.assertEqual(snap()['visibleMeshes'], 8)
                page.uncheck('#veins'); self.assertEqual(snap()['visibleMeshes'], 0)
                page.click('#reset'); self.assertEqual(snap()['visibleMeshes'], 31)
                page.uncheck('#colors'); page.check('#colors')
                before = snap()['camera']; page.click('#left'); self.assertNotEqual(before, snap()['camera'])
                page.click('#right')
                z = snap()['zoom']; page.click('#zoom-in'); self.assertGreater(snap()['zoom'], z)
                page.click('#zoom-out'); self.assertAlmostEqual(snap()['zoom'], z)
                self.assertTrue(all(m['matrix'] == [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1] for m in snap()['meshes']))
                box = page.locator('#viewport').bounding_box()
                page.mouse.move(box['x'] + 100, box['y'] + 100); page.mouse.down(); page.mouse.move(box['x'] + 180, box['y'] + 140, steps=8); page.mouse.up()
                self.assertNotEqual(initial['camera'], snap()['camera'])
                page.set_viewport_size({'width': 390, 'height': 844})
                page.click('#reset')
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                page.locator('#viewport').screenshot(path=str(evidence / 'mobile.png'))
                self.assertEqual(snap()['visibleMeshes'], 31)
                self.assertEqual(errors, [])
                (evidence / 'runtime.json').write_text(json.dumps({'initial': initial, 'mobile': snap(), 'selected_tested': names, 'consoleErrors': errors}, indent=2))
                fallback = browser.new_page()
                await_errors = []
                fallback.on('pageerror', lambda e: await_errors.append(str(e)))
                fallback.route('**/3d-vh-f-blood-vasculature.glb', lambda route: route.fulfill(status=404, body='Missing'))
                fallback.goto(url)
                fallback.wait_for_function("document.querySelector('#status').textContent.includes('Não foi possível')")
                self.assertFalse(fallback.evaluate('window.coronaryReference.snapshot().ready'))
                self.assertTrue(fallback.locator('#controls').evaluate('(e)=>e.disabled'))
                self.assertTrue(fallback.locator('#wall').is_disabled())
                with fallback.expect_navigation(): fallback.click('#original')
                self.assertIn('atlas.html', fallback.url)
                self.assertEqual(await_errors, [])
                browser.close()
        finally:
            server.shutdown()
            server.server_close()

if __name__ == '__main__':
    unittest.main()
