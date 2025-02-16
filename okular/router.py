from okular.views.job import job_blueprint
from okular.views.job_dashboard import job_dashboard_blueprint
from okular.views.jobs import jobs_blueprint
from okular.views.update import update_blueprint

class Router:
    def __init__(self, app):
        app.register_blueprint(update_blueprint)
        app.register_blueprint(jobs_blueprint)
        app.register_blueprint(job_blueprint)
        app.register_blueprint(job_dashboard_blueprint)
