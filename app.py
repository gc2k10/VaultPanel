"""Read-only review application; importing it never starts a server."""
import hmac
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request
from config import settings
import collectors
from hardware import disabled_operation


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(TRUSTED_HOSTS=['localhost', '127.0.0.1', '[::1]'],
                      MAX_CONTENT_LENGTH=4096, ACCESS_TOKEN=settings.access_token)
    if config:
        app.config.update(config)

    @app.before_request
    def guard():
        # No proxy header trust. Local-only even when another WSGI server is used.
        if request.remote_addr not in {'127.0.0.1', '::1'}:
            return jsonify(ok=False, error='Local access only'), 403
        token = app.config['ACCESS_TOKEN']
        if token:
            auth = request.authorization
            supplied = auth.password if auth and auth.type == 'basic' else ''
            if not supplied or not hmac.compare_digest(supplied.encode(), token.encode()):
                return ('Authentication required', 401,
                        {'WWW-Authenticate': 'Basic realm="VaultPanel", charset="UTF-8"'})

    @app.after_request
    def headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        return response

    @app.get('/')
    def index():
        return render_template('index.html', title='VaultPanel')

    @app.get('/retro')
    def retro():
        return render_template('index_retro.html', title='VaultPanel Retro')

    for name in ('overview', 'cooling', 'storage', 'services', 'network'):
        def read(name=name):
            return jsonify(getattr(collectors, 'get_' + name)())
        app.add_url_rule('/api/' + name, name, read, methods=['GET'])

    @app.get('/api/alerts')
    def alerts():
        payload = collectors.get_alerts()
        return jsonify(alerts=payload['alerts'], history=[],
                       generated_at=datetime.now(timezone.utc).isoformat())

    @app.get('/api/system')
    def system():
        # The old endpoint executed a deployment-specific shell script.
        return jsonify(collectors.get_overview())

    @app.get('/api/capabilities')
    def capabilities():
        return jsonify(read_only=True, hardware_writes=False, backups=False,
                       command_reads=settings.command_reads)

    for name in ('backup', 'led', 'fans', 'oled'):
        def disabled(name=name):
            return jsonify(disabled_operation(name)), 403
        app.add_url_rule('/api/' + name, name, disabled, methods=['POST'])
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090, debug=False)
