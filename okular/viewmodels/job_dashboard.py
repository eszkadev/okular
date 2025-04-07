from datetime import date, timedelta
from okular import dbcontext
from okular.db.models import Builds, BuildFails
from okular.viewmodels.base import BaseViewModel
from dataclasses import dataclass
from sqlalchemy import func

@dataclass
class JobDashboardViewModel(BaseViewModel):
    jenkins_job: str
    fails: []
    build_fails_count: int
    builds_count: int
    success_rate: str

    def __init__(self, jenkins_api, last_update_str, jenkins_job):
        self.jenkins_api = jenkins_api
        self.last_update_str = last_update_str
        self.navbar_right = 'Job: ' + jenkins_job
        self.jenkins_job = jenkins_job

        last_week_date = date.today() + timedelta(days=-7)
        build_fails = (dbcontext.session.query(Builds).join(BuildFails)
                        .with_entities(Builds.id, BuildFails.test_name, func.count(BuildFails.test_name))
                        .where(BuildFails.test_name != '')
                        .filter(Builds.date.between(last_week_date, date.today()))
                        .group_by(BuildFails.test_name)
                        .order_by(func.count(BuildFails.test_name).desc())
                        .limit(10)
                        .all())

        self.build_fails_count = (dbcontext.session.query(Builds).join(BuildFails)
                        .with_entities(Builds.id, BuildFails.test_name, func.count(BuildFails.test_name))
                        .where(BuildFails.test_name != '')
                        .filter(Builds.date.between(last_week_date, date.today()))
                        .group_by(Builds.id)
                        .count())

        self.builds_count = (dbcontext.session.query(Builds)
                        .filter(Builds.date.between(last_week_date, date.today()))
                        .count())

        if self.builds_count > 0:
            self.success_rate = str(int(100 - self.build_fails_count / self.builds_count * 100)) + '%'
        else:
            self.success_rate = 'N/A'

        self.fails = []
        for fail in build_fails:
            entry = {'test_name': fail[1], 'count': fail[2]}
            self.fails.append(entry)
