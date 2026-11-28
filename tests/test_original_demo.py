"""Static preview has no application imports and exports only reviewed assets."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class OriginalDemoTests(unittest.TestCase):
    def test_static_export_without_collectors_or_commands(self):
        spec = importlib.util.spec_from_file_location('original_demo', ROOT / 'scripts/build-original-demo.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp, patch('subprocess.Popen', side_effect=AssertionError('No commands')), patch.dict('sys.modules', {'app': None, 'collectors': None, 'hardware': None}):
            dest = Path(tmp) / 'preview'
            module.build(dest)
            files = {str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}
            self.assertEqual(files, {'index.html', 'retro.html', 'preview.js', 'preview-data.js', 'preview.css'} | {'static/' + a for a in module.ASSETS})
            for layout in ('index', 'retro'):
                html = (dest / (layout + '.html')).read_text()
                self.assertIn("connect-src 'none'", html)
                self.assertIn('DEMO — SYNTHETIC DATA ONLY', html)
                self.assertNotIn('href="/"', html)
                self.assertNotIn('{{', html)
                self.assertLess(html.index('src="preview.js"'), html.index('src="static/js/app'))
            for asset in module.ASSETS:
                self.assertEqual((dest / 'static' / asset).read_bytes(), (ROOT / 'static' / asset).read_bytes())
            with self.assertRaises(FileExistsError):
                module.build(dest)
