"""Focused real-browser regression; requires the static site on :8876.

Run: PYTHONPATH=scripts/tests /home/victorzera/Estudos/atlas-qa-venv/bin/python -m unittest test_3d_initialization -v
Only the real HRA atlas is loaded; no model/catalog fixtures replace assets.
"""
import os
import unittest

from playwright.sync_api import sync_playwright


BASE = os.environ.get('ATLAS_URL', 'http://127.0.0.1:8876').rstrip('/')


class Initialization3D(unittest.TestCase):
    def test_resize_between_catalog_and_meshes_then_labels_after_ready(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=[
                '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            ])
            page = browser.new_page(
                viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce',
            )
            errors = []
            pending = []
            # Register before navigation so startup failures cannot be missed.
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.route('**/*', lambda route: route.continue_()
                       if route.request.url.startswith(BASE + '/') else route.abort())

            def observe_module(route):
                response = route.fetch()
                # Read-only visibility into lexical initialization state. The
                # served module's behavior and real catalog/GLB are unchanged.
                route.fulfill(response=response, body=response.text() + '''
window.__initializationProbe = () => ({ready: state.ready,
    catalogLoaded: Boolean(catalog), entries: entries.length,
    meshes: meshes.size, labels: state.labels});
''')

            page.route('**/app.js', observe_module)
            page.route('**/assets/heart-hra/model.glb', lambda route: pending.append(route))
            try:
                page.goto(BASE + '/atlas.html?detail=hra', wait_until='domcontentloaded')
                page.wait_for_function('window.__initializationProbe?.().catalogLoaded')
                # Pump browser events until the real loader requests its GLB,
                # retaining the response indefinitely rather than racing a timer.
                for _ in range(300):
                    if pending:
                        break
                    page.wait_for_timeout(20)
                self.assertEqual(len(pending), 1, 'Real GLB request was not intercepted')
                before = page.evaluate('__initializationProbe()')
                self.assertEqual(before, {
                    'ready': False, 'catalogLoaded': True, 'entries': 14,
                    'meshes': 0, 'labels': False,
                })
                old_width = page.locator('#viewer').evaluate('(el) => el.clientWidth')
                page.set_viewport_size({'width': 1200, 'height': 900})
                page.wait_for_function(
                    "old => document.querySelector('#viewer').clientWidth !== old", arg=old_width,
                )
                page.evaluate('''() => new Promise(resolve =>
                    requestAnimationFrame(() => requestAnimationFrame(resolve)))''')
                self.assertEqual(page.evaluate('__initializationProbe()'), before)
                print('PENDING:', before, 'pageerrors:', errors, flush=True)
                self.assertEqual(errors, [], 'Uncaught errors while catalog exists but meshes are pending')

                pending.pop().continue_()
                page.wait_for_function(
                    'window.heartStudy && window.heartViewer?.snapshot().drawCalls > 0',
                    timeout=90000,
                )
                ready = page.evaluate('heartViewer.snapshot()')
                self.assertTrue(ready['ready'])
                self.assertEqual(ready['parts'], 14)
                page.locator('#labels').click()
                page.wait_for_function("document.querySelectorAll('.mesh-label:not([hidden])').length > 0")
                self.assertTrue(page.evaluate('heartViewer.snapshot().labels'))
                self.assertTrue(page.locator('#label-status').is_visible())
                visible_labels = page.locator('.mesh-label:visible').all_text_contents()
                self.assertTrue(visible_labels)
                self.assertEqual(errors, [], 'Uncaught initialization or label errors')
                print('READY:', {'parts': ready['parts'], 'drawCalls': ready['drawCalls'],
                                 'labels': visible_labels, 'pageerrors': errors}, flush=True)
            finally:
                for route in pending:
                    route.abort()
                page.close()
                browser.close()
