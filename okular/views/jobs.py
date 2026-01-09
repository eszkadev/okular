import flask
from flask import Blueprint, render_template
from okular.viewmodels.jobs import JobsViewModel
from okular.views import get_last_update_string

jobs_blueprint = Blueprint("jobs", __name__, template_folder='templates')

@jobs_blueprint.route('/jobs')
def jobs():
    last_update_str = get_last_update_string()
    jobs_view_model = JobsViewModel(
        jenkins_host=flask.current_app.config['JENKINS_HOST'],
        jenkins_api=flask.current_app.config['JENKINS_API'],
        last_update_str=last_update_str
    )

    return render_template('jobs.html', **jobs_view_model.as_dict())