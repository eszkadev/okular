import flask
from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, render_template, request
from okular.views import get_last_update_string
from okular.viewmodels.job_dashboard import JobDashboardViewModel, query_fail_summary, success_rate_percent

job_dashboard_blueprint = Blueprint("job_dashboard", __name__, template_folder='templates')

@job_dashboard_blueprint.route('/job/<job>/dashboard')
def job_dashboard(job):
    last_update_str = get_last_update_string()

    job_dashboard_view_model = JobDashboardViewModel(
        jenkins_host = flask.current_app.config['JENKINS_HOST'],
        jenkins_job = job,
        last_update_str = last_update_str
    )

    return render_template('job_dashboard.html', **job_dashboard_view_model.as_dict())


@job_dashboard_blueprint.route('/api/job/<job>/dashboard')
def job_dashboard_api(job):
    """JSON summary of one day: every failing test, not only the top 10.

    Query parameter `date` selects the day as YYYY-MM-DD; defaults to today.
    """
    date_arg = request.args.get('date')
    if date_arg is None:
        day = date.today()
    else:
        try:
            day = date.fromisoformat(date_arg)
        except ValueError:
            return jsonify({'error': 'Invalid date, expected YYYY-MM-DD'}), 400

    start = datetime.combine(day, datetime.min.time())
    summary = query_fail_summary(start, start + timedelta(days=1))

    return jsonify({
        'job': job,
        'date': day.isoformat(),
        'builds_count': summary['builds_count'],
        'build_fails_count': summary['build_fails_count'],
        'success_rate': success_rate_percent(summary['builds_count'], summary['build_fails_count']),
        'fails': summary['fails'],
    })
