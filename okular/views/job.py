import flask
from flask import Blueprint, request
from okular.views import get_last_update_string
from okular.views.base import BaseView
from okular.viewmodels.job import JobViewModel

job_blueprint = Blueprint("job", __name__, template_folder='templates')

class JobView(BaseView):
    def __init__(self, job_view_model):
        super().__init__(job_view_model)

    def generateHTML(self, body = ''):
        builds_html = f''

        for build in self.model.builds:
            fails = f''
            for fail in build.fails:
                fails = f'{fails}<li class="list-group-item">{fail.name}</li>'

            status_class = ''
            if build.status == 'SUCCESS':
                status_class = 'bg-success text-light'
            elif build.status == 'FAILURE':
                status_class = 'bg-danger text-light'

            builds_html = f'{builds_html}<div class="card" style="width: 95%; margin: 10px auto;"><h4 class="card-header {status_class}"><a href="{build.url}">{build.id}</a>: {build.name}</h4><div class="card-body"><p>{build.date} {build.status}</p><ul class="list-group list-group-flush">{fails}</ul></div></div>'

        self.model.navbar_right = f'Job: {self.model.jenkins_job}'

        pages = ''
        previous = self.model.page - 1
        next = self.model.page + 1
        if self.model.page > 0:
            pages = pages + f'<li class="page-item"><a class="page-link" href="/?page={previous}">Previous</a></li>'
        if self.model.count > self.model.limit * (self.model.page + 1):
            pages = pages + f'<li class="page-item"><a class="page-link" href="/?page={next}">Next</a></li>'

        body_html = f'{builds_html}<nav class="d-flex justify-content-center flex-nowrap"><ul class="pagination">{pages}</ul></nav>'

        return super().generateHTML(body_html)

@job_blueprint.route('/job')
def job():
    last_update_str = get_last_update_string()
    limit = 15

    args = request.args
    page = args.get('page')

    job_view_model = JobViewModel(
        jenkins_api = flask.current_app.config['JENKINS_API'],
        jenkins_job = flask.current_app.config['JENKINS_JOB'],
        last_update_str = last_update_str,
        page = page,
        limit = limit
    )
    view = JobView(job_view_model)
    return view.generateHTML()