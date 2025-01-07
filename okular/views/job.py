import dataclasses

import flask
from flask import Blueprint, render_template, request
from okular.views import get_last_update_string
from okular.viewmodels.job import JobViewModel

job_blueprint = Blueprint("job", __name__, template_folder='templates')

@job_blueprint.route('/') #job/<job>
def job():
    last_update_str = get_last_update_string()
    limit = 15

    args = request.args
    page = args.get('page')

    job_view_model = JobViewModel(
        jenkins_api = flask.current_app.config['JENKINS_API'],
        jenkins_job = flask.current_app.config['JENKINS_JOB'],
        last_update_str = last_update_str,
        page = page,
        limit = limit
    )

    return render_template('job.html', **(dataclasses.asdict(job_view_model)))