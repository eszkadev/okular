import jenkinsapi
import html

from flask import Flask
from jenkinsapi.jenkins import Jenkins

def create_app(jenkins_api, jenkins_job):
    app = Flask(__name__)

    @app.route("/")
    def index():
        J = Jenkins(jenkins_api)
        job = J[jenkins_job];
        build = job[job.get_last_failed_buildnumber()]
        console = html.escape(build.get_console())

        return f'<h1>okular</h1><p>Watching: {jenkins_api}, {jenkins_job}</p><p>Last failed build: {build}</p><textarea style="width: 100%; height: 350px;">{console}</textarea>'

    return app