from okular.viewmodels.base import BaseViewModel

class JobViewModel(BaseViewModel):
    def __init__(self, jenkins_api, last_update_str, jenkins_job, page, count, limit, builds):
        super().__init__(jenkins_api, last_update_str)
        self.jenkins_job = jenkins_job
        self.page = page
        self.count = count
        self.limit = limit
        self.builds = builds