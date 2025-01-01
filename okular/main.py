import okular
import flask
from flask import Flask
from okular.router import Router

def create_app(jenkins_api, jenkins_job):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okular.sqlite3'

    okular.dbcontext.init_app(app)

    with app.app_context():
        okular.dbcontext.create_all()

        app.config['JENKINS_API'] = jenkins_api
        app.config['JENKINS_JOB'] = jenkins_job
        flask.g.router = Router(app)

    return app