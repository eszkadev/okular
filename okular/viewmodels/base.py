class BaseViewModel:
    def __init__(self, jenkins_api, last_update_str):
        self.jenkins_api = jenkins_api
        self.last_update_str = last_update_str
        self.navbar_right = ''