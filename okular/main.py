import okular
import flask
from flask import Flask
from okular.router import Router
from urllib.parse import urlparse

def create_app(jenkins_api, jenkins_job):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okular.sqlite3'

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