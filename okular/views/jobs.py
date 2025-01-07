import flask
from flask import Blueprint, render_template
from jenkinsapi.jenkins import Jenkins

from okular.views import get_last_update_string

jobs_blueprint = Blueprint("jobs", __name__, template_folder='templates')

@jobs_blueprint.route('/')
def jobs():
    j = Jenkins(flask.current_app.config['JENKINS_API'])
    available_jobs = []
    for item in j.jobs.iterkeys():
        available_jobs.append(item)

    return render_template('jobs.html',
                           jenkins_api = flask.current_app.config['JENKINS_API'],
                           last_update_str = get_last_update_string(),
                           navbar_right = '',
                           available_jobs = available_jobs)