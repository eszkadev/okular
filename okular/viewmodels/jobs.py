from dataclasses import dataclass
from jenkinsapi.jenkins import Jenkins
from okular.viewmodels.base import BaseViewModel

@dataclass
class JobsViewModel(BaseViewModel):
    available_jobs: []

    def __init__(self, jenkins_api, last_update_str):
        self.jenkins_api = jenkins_api
        self.last_update_str = last_update_str
        self.navbar_right = ''

        j = Jenkins(jenkins_api)
        self.available_jobs = []
        for item in j.jobs.iterkeys():
            self.available_jobs.append(item)
