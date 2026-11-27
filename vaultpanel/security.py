"""Local, authenticated, read-only boundary for the source-intake build."""
import hmac
import os
from urllib.parse import urlsplit
from flask import jsonify, request


def protect_app(app):
    app.config['MAX_CONTENT_LENGTH'] = 16384

    @app.before_request
    def authorize():
        if urlsplit(request.host_url).hostname not in {'localhost', '127.0.0.1', '::1'}:
            return jsonify(error='Use the loopback address or an SSH tunnel'), 400
        password = os.environ.get('VAULTPANEL_PASSWORD', '')
        if len(password) < 32 or password == 'REPLACE_ME':
            return jsonify(error='Set a unique VAULTPANEL_PASSWORD of at least 32 characters'), 503
        auth = request.authorization
        if (not auth or auth.type.lower() != 'basic'
                or not hmac.compare_digest((auth.username or '').encode(), b'vaultpanel')
                or not hmac.compare_digest((auth.password or '').encode(), password.encode())):
            return jsonify(error='Authentication required'), 401, {
                'WWW-Authenticate': 'Basic realm="VaultPanel", charset="UTF-8"'
            }
        # No enable switch: privileged actions need a separate review.
        if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
            return jsonify(ok=False, error='Hardware actions and backups are disabled in the intake build'), 403

    @app.after_request
    def headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return response
