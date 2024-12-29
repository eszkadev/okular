from okular import dbcontext
from okular.db.models import Builds
from okular.viewmodels.base import BaseViewModel

class JobViewModel(BaseViewModel):
    def __init__(self, jenkins_api, last_update_str, jenkins_job, page, limit):
        super().__init__(jenkins_api, last_update_str)
        self.jenkins_job = jenkins_job
        self.limit = limit

        if page is None:
            self.page = 0
        else:
            self.page = int(page)

        self.builds = Builds.query.order_by(Builds.id.desc()).offset(self.page * self.limit).limit(self.limit).all()
        self.count = dbcontext.session.query(Builds).count()