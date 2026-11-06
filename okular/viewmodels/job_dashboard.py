from datetime import date, datetime, timedelta
from okular import dbcontext
from okular.db.models import Builds, BuildFails
from okular.viewmodels.base import BaseViewModel
from dataclasses import dataclass
from sqlalchemy import func


def query_fail_summary(start, end, limit=None):
    """Summarise the builds whose date lies in [start, end).

    Returns a dict with the number of builds, the number of failed builds
    and the per-test fail counts ordered by count, descending. `limit`
    caps the number of tests returned; None returns every test.
    """
    in_window = (Builds.date >= start) & (Builds.date < end)

    fails_query = (dbcontext.session.query(Builds).join(BuildFails)
                    .with_entities(BuildFails.test_name, func.count(BuildFails.test_name))
                    .where(BuildFails.test_name != '')
                    .filter(in_window)
                    .group_by(BuildFails.test_name)
                    .order_by(func.count(BuildFails.test_name).desc(), BuildFails.test_name))
    if limit is not None:
        fails_query = fails_query.limit(limit)

    build_fails_count = (dbcontext.session.query(Builds).join(BuildFails)
                    .with_entities(Builds.id)
                    .where(BuildFails.test_name != '')
                    .filter(in_window)
                    .group_by(Builds.id)
                    .count())

    builds_count = (dbcontext.session.query(Builds)
                    .filter(in_window)
                    .count())

    return {
        'builds_count': builds_count,
        'build_fails_count': build_fails_count,
        'fails': [{'test_name': name, 'count': count} for name, count in fails_query.all()],
    }


def success_rate_percent(builds_count, build_fails_count):
    """Integer percentage of builds without fails, or None without builds."""
    if builds_count <= 0:
        return None
    return int(100 - build_fails_count / builds_count * 100)


@dataclass
class JobDashboardViewModel(BaseViewModel):
    jenkins_job: str
    fails: []
    build_fails_count: int
    builds_count: int
    success_rate: str

    def __init__(self, jenkins_host, last_update_str, jenkins_job):
        self.jenkins_host = jenkins_host
        self.last_update_str = last_update_str
        self.navbar_right = 'Job: ' + jenkins_job
        self.jenkins_job = jenkins_job

        # Last week up to and including today.
        today = datetime.combine(date.today(), datetime.min.time())
        summary = query_fail_summary(today + timedelta(days=-7), today + timedelta(days=1), limit=10)

        self.build_fails_count = summary['build_fails_count']
        self.builds_count = summary['builds_count']
        self.fails = summary['fails']

        rate = success_rate_percent(self.builds_count, self.build_fails_count)
        self.success_rate = 'N/A' if rate is None else str(rate) + '%'
