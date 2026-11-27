from pathlib import Path
import ast
import struct
import types
import unittest
from unittest.mock import Mock
import zlib

ROOT = Path(__file__).resolve().parents[1]


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

    def test_manifest_icons_resolve(self):
        import json
        from urllib.parse import urljoin
        from app import create_app
        client = create_app({'ACCESS_TOKEN': ''}).test_client()
        with client.get('/static/site.webmanifest') as response:
            manifest = json.loads(response.data)
        self.assertEqual(manifest['name'], 'VaultPanel')
        for item in manifest['icons']:
            with client.get(urljoin('/static/site.webmanifest', item['src'])) as response:
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.data.startswith(b'\x89PNG\r\n\x1a\n'))
