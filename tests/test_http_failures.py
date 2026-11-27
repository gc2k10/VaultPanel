import base64
import unittest
from unittest.mock import patch

import collectors
from app import create_app


class HTTPFailureTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app({'TESTING': True, 'ACCESS_TOKEN': ''}).test_client()

    def test_collector_failure_is_generic_json_without_details(self):
        for endpoint, function in [('overview', 'get_overview'), ('cooling', 'get_cooling'),
                                   ('storage', 'get_storage'), ('services', 'get_services'),
                                   ('network', 'get_network'), ('alerts', 'get_alerts'),
                                   ('system', 'get_overview')]:
            with self.subTest(endpoint=endpoint), patch.object(collectors, function, side_effect=RuntimeError('private-test-detail')):
                response = self.client.get('/api/' + endpoint)
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json, {'ok': False, 'error': 'Telemetry unavailable'})
                self.assertNotIn(b'private-test-detail', response.data)
                self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_invalid_authentication_is_rejected_before_telemetry(self):
        client = create_app({'TESTING': True, 'ACCESS_TOKEN': 'test-only'}).test_client()
        with patch.object(collectors, 'get_overview') as collector:
            for authorization in ['Basic !invalid!', 'Bearer test-only', 'Basic ' + base64.b64encode(b'user:wrong').decode(), 'Basic ' + base64.b64encode(b'user').decode()]:
                response = client.get('/api/overview', headers={'Authorization': authorization})
                self.assertEqual(response.status_code, 401)
                self.assertNotIn(b'test-only', response.data)
            collector.assert_not_called()

    def test_unsupported_methods_and_traversal_do_not_run_collectors(self):
        with patch.object(collectors, 'get_overview') as collector, patch('subprocess.Popen') as process:
            for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                self.assertEqual(self.client.open('/api/overview', method=method).status_code, 405)
            for endpoint in ['backup', 'fans', 'led', 'oled']:
                self.assertEqual(self.client.get('/api/' + endpoint).status_code, 405)
            for path in ['/static/../config.py', '/static/%2e%2e/config.py', '/api/missing']:
                self.assertEqual(self.client.get(path).status_code, 404)
            collector.assert_not_called()
            process.assert_not_called()

    def test_cross_origin_read_is_not_cors_enabled(self):
        response = self.client.get('/api/capabilities', headers={'Origin': 'https://example.invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn("frame-ancestors 'none'", response.headers['Content-Security-Policy'])

    def test_forwarded_headers_do_not_override_host_or_client(self):
        headers = {'Host': 'untrusted.invalid', 'X-Forwarded-Host': 'localhost', 'X-Forwarded-For': '127.0.0.1', 'Forwarded': 'for=127.0.0.1;host=localhost'}
        self.assertEqual(self.client.get('/api/capabilities', headers=headers).status_code, 400)
        headers['Host'] = 'localhost'
        self.assertEqual(self.client.get('/api/capabilities', headers=headers, environ_overrides={'REMOTE_ADDR': '192.0.2.1'}).status_code, 403)

    def test_malformed_and_oversized_admin_bodies_are_denied(self):
        with patch('subprocess.Popen') as process:
            for body in ['{', 'x' * 65536]:
                response = self.client.post('/api/fans', data=body, content_type='application/json')
                self.assertEqual(response.status_code, 403)
                self.assertFalse(response.json['ok'])
            process.assert_not_called()
