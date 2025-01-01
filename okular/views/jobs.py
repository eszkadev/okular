import flask
from flask import Blueprint
from okular.views import get_last_update_string
from okular.views.base import BaseView
from okular.viewmodels.base import BaseViewModel

jobs_blueprint = Blueprint("jobs", __name__, template_folder='templates')

class JobsView(BaseView):
    def __init__(self, model):
        super().__init__(model)

    def generateHTML(self, body = ''):
        body = ''
        return super().generateHTML(body)

@jobs_blueprint.route('/')
def jobs():
    last_update_str = get_last_update_string()

    jobs_view_model = BaseViewModel(
        jenkins_api = flask.current_app.config['JENKINS_API'],
        last_update_str = last_update_str
    )

    view = JobsView(jobs_view_model)
    return view.generateHTML()