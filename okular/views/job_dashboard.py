import flask
from datetime import date, datetime, timedelta
from flask import Blueprint, Response, render_template, request
from okular.views import get_last_update_string
from okular.viewmodels.job_dashboard import JobDashboardViewModel, query_fail_summary, success_rate_percent

job_dashboard_blueprint = Blueprint("job_dashboard", __name__, template_folder='templates')

PROMETHEUS_CONTENT_TYPE = 'text/plain; version=0.0.4; charset=utf-8'

@job_dashboard_blueprint.route('/job/<job>/dashboard')
def job_dashboard(job):
    last_update_str = get_last_update_string()

    job_dashboard_view_model = JobDashboardViewModel(
        jenkins_host = flask.current_app.config['JENKINS_HOST'],
        jenkins_job = job,
        last_update_str = last_update_str
    )

    return render_template('job_dashboard.html', **job_dashboard_view_model.as_dict())


def prometheus_label_value(value):
    """Quote a label value the way the text exposition format requires."""
    escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return '"' + escaped + '"'


def prometheus_sample(name, labels, value):
    pairs = ','.join('%s=%s' % (key, prometheus_label_value(val)) for key, val in labels.items())
    return '%s{%s} %s' % (name, pairs, value)


@job_dashboard_blueprint.route('/api/job/<job>/dashboard')
def job_dashboard_api(job):
    """One day's summary in the Prometheus text exposition format.

    Every failing test is listed, not only the top 10 of the dashboard page.
    Query parameter `date` selects the day as YYYY-MM-DD; defaults to today.
    """
    date_arg = request.args.get('date')
    if date_arg is None:
        day = date.today()
    else:
        try:
            day = date.fromisoformat(date_arg)
        except ValueError:
            return Response('Invalid date, expected YYYY-MM-DD\n', status=400, mimetype='text/plain')

    start = datetime.combine(day, datetime.min.time())
    summary = query_fail_summary(start, start + timedelta(days=1))
    rate = success_rate_percent(summary['builds_count'], summary['build_fails_count'])

    # The label is named jenkins_job because Prometheus attaches its own job label to every scraped sample.
    labels = {'jenkins_job': job, 'date': day.isoformat()}

    lines = [
        '# HELP okular_day_builds Number of builds that started on the day.',
        '# TYPE okular_day_builds gauge',
        prometheus_sample('okular_day_builds', labels, summary['builds_count']),
        '# HELP okular_day_failed_builds Number of builds on the day with at least one failed test.',
        '# TYPE okular_day_failed_builds gauge',
        prometheus_sample('okular_day_failed_builds', labels, summary['build_fails_count']),
        '# HELP okular_day_success_rate_percent Percentage of builds on the day without failed tests.',
        '# TYPE okular_day_success_rate_percent gauge',
    ]
    if rate is not None:
        lines.append(prometheus_sample('okular_day_success_rate_percent', labels, rate))

    lines.append('# HELP okular_day_test_failures Number of builds on the day in which the test failed.')
    lines.append('# TYPE okular_day_test_failures gauge')
    for fail in summary['fails']:
        lines.append(prometheus_sample('okular_day_test_failures', dict(labels, test=fail['test_name']), fail['count']))

    return Response('\n'.join(lines) + '\n', content_type=PROMETHEUS_CONTENT_TYPE)
