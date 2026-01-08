from okular import dbcontext
from okular.db.models import Builds
from okular.viewmodels.base import BaseViewModel
from dataclasses import dataclass

@dataclass
class JobViewModel(BaseViewModel):
    jenkins_job: str
    page: int
    limit: int
    count: int
    builds: []

    def __init__(self, jenkins_api, last_update_str, jenkins_job, page, limit):
        self.jenkins_api = jenkins_api
        self.last_update_str = last_update_str
        self.navbar_right = 'Job: ' + jenkins_job
        self.jenkins_job = jenkins_job
        self.limit = limit

        if page is None:
            self.page = 0
        else:
            try:
                self.page = max(0, int(page))
            except (ValueError, TypeError):
                self.page = 0

        builds = Builds.query.order_by(Builds.id.desc()).offset(self.page * self.limit).limit(self.limit).all()
        self.count = dbcontext.session.query(Builds).count()

        self.builds = []
        for build in builds:
            status_class = ''
            if build.status == 'SUCCESS':
                status_class = 'bg-success text-light'
            elif build.status == 'FAILURE':
                status_class = 'bg-danger text-light'

            fails = []
            for fail in build.fails:
                fails.append(fail.name)

            entry = {'build': build, 'status_class': status_class, 'fails': fails}
            self.builds.append(entry)