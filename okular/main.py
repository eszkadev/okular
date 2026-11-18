import okular
import flask
from flask import Flask
from okular.router import Router
from urllib.parse import urlparse

# The pages run no script. Their only outside resource is the Bootstrap stylesheet, and the
# cards in job.html carry a style attribute.
CONTENT_SECURITY_POLICY = '; '.join([
    "default-src 'none'",
    "style-src https://cdn.jsdelivr.net 'unsafe-inline'",
    "img-src 'self' data:",
    "base-uri 'none'",
    "form-action 'self'",
    "frame-ancestors 'none'",
])


def add_security_headers(response):
    response.headers['Content-Security-Policy'] = CONTENT_SECURITY_POLICY
    return response


def create_app(jenkins_api, jenkins_job, database_uri='sqlite:///okular.sqlite3'):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.after_request(add_security_headers)

    okular.dbcontext.init_app(app)

    with app.app_context():
        okular.dbcontext.create_all()

        app.config['JENKINS_API'] = jenkins_api
        app.config['JENKINS_JOB'] = jenkins_job

        # Extract hostname for safe display in UI (no credentials)
        parsed = urlparse(jenkins_api)
        app.config['JENKINS_HOST'] = parsed.hostname or ''

        flask.g.router = Router(app)

    return app
