import flask
from flask import Blueprint, render_template
from okular.views import get_last_update_string
from okular.viewmodels.job_dashboard import JobDashboardViewModel

job_dashboard_blueprint = Blueprint("job_dashboard", __name__, template_folder='templates')

@job_dashboard_blueprint.route('/job/<job>/dashboard')
def job_dashboard(job):
    last_update_str = get_last_update_string()

    job_dashboard_view_model = JobDashboardViewModel(
        jenkins_api = flask.current_app.config['JENKINS_API'],
        jenkins_job = job,
        last_update_str = last_update_str
    )

    return render_template('job_dashboard.html', **job_dashboard_view_model.as_dict())