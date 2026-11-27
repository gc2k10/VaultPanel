from pathlib import Path
import ast
import struct
import types
import unittest
from unittest.mock import Mock
import zlib

ROOT = Path(__file__).resolve().parents[1] / 'vaultpanel'


class AssetTests(unittest.TestCase):
    def test_pngs_have_valid_crcs_and_only_reviewed_chunks(self):
        allowed = {b'IHDR', b'PLTE', b'tRNS', b'IDAT', b'IEND', b'sRGB', b'gAMA', b'cHRM'}
        paths = list((ROOT / 'static').rglob('*.png'))
        self.assertEqual(len(paths), 6)
        for path in paths:
            data = path.read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
            offset = 8
            kinds = []
            while offset < len(data):
                size = struct.unpack('>I', data[offset:offset + 4])[0]
                kind = data[offset + 4:offset + 8]
                payload = data[offset + 8:offset + 8 + size]
                crc = struct.unpack('>I', data[offset + 8 + size:offset + 12 + size])[0]
                self.assertIn(kind, allowed, str(path))
                self.assertEqual(zlib.crc32(kind + payload) & 0xffffffff, crc)
                kinds.append(kind)
                offset += size + 12
            self.assertEqual(offset, len(data))
            self.assertEqual(kinds[0], b'IHDR')
            self.assertEqual(kinds[-1], b'IEND')

    def test_oled_missing_logo_falls_back_without_opening_image_or_hardware(self):
        # Compile only the drawing function: never import hardware initialization.
        for name, expected in [('vaultpanel_oled.py', 'VaultPanel'),
                               ('vaultpanel_oled_custom.py', ['VaultPanel'])]:
            tree = ast.parse((ROOT / 'scripts' / name).read_text())
            function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'draw_logo')
            draw = Mock()
            image = Mock()
            namespace = {'os': types.SimpleNamespace(path=types.SimpleNamespace(exists=lambda _: False)),
                         'LOGO_PATH': 'missing.png', 'draw_text': draw, 'Image': image}
            exec(compile(ast.Module(body=[function], type_ignores=[]), name, 'exec'), namespace)
            namespace['draw_logo']()
            draw.assert_called_once_with(expected)
            image.open.assert_not_called()
