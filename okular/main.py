import html
import jenkinsapi

from datetime import datetime
from flask import Flask, request
from jenkinsapi.jenkins import Jenkins
from okular import dbcontext
from okular.parser import Parser

from okular.db.models import Builds, BuildFails, Settings, Tests

from okular.viewmodels.base import BaseViewModel
from okular.viewmodels.job import JobViewModel

from okular.views.job import JobView
from okular.views.jobs import JobsView

def get_last_update_string():
    last_update = Settings.query.filter_by(name='last_update').first()
    last_update_str = '-'
    if not last_update is None:
        last_update_str = last_update.value
    return last_update_str

def create_app(jenkins_api, jenkins_job):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okular.sqlite3'
    dbcontext.init_app(app)

    with app.app_context():
        dbcontext.create_all()

    @app.route('/')
    def main():
        last_update_str = get_last_update_string();

        jobs_view_model = BaseViewModel(
            jenkins_api = jenkins_api,
            last_update_str = last_update_str
        )

        view = JobsView(jobs_view_model)
        return view.generateHTML()

    @app.route('/job')
    def index():
        args = request.args
        last_update_str = get_last_update_string()

        limit = 15
        page = args.get('page')
        if page is None:
            page = 0
        else:
            page = int(page)

        builds = Builds.query.order_by(Builds.id.desc()).offset(page*limit).limit(limit).all()
        count = dbcontext.session.query(Builds).count()

        job_view_model = JobViewModel(
            jenkins_api = jenkins_api,
            jenkins_job = jenkins_job,
            last_update_str = last_update_str,
            page = page,
            count = count,
            limit = limit,
            builds = builds
        )
        view = JobView(job_view_model)
        return view.generateHTML()

    @app.route('/update')
    def update():
        J = Jenkins(jenkins_api)
        job = J[jenkins_job]
        builds = job.get_build_dict()
        count = 0
        found = 0
        for build_number in builds:
            found = found + 1
            url = builds[build_number]
            build = Builds.query.filter_by(id=build_number).first()
            if build is None:
                jenkins_build = job[build_number]
                status = jenkins_build.get_status()
                name = jenkins_build.get_description()
                date = jenkins_build.get_timestamp()

                if status == None:
                    continue

                build = Builds(id=build_number, status=status, name=name, url=url, date=date)
                dbcontext.session.add(build)
                count = count + 1

                console = html.escape(jenkins_build.get_console())
                parser = Parser(console)
                parser.parse()
                fails = parser.get_fails()

                for test_name in fails:
                    test = Tests.query.filter_by(name=test_name).first()
                    if test is None:
                        test = Tests(name=test_name)
                        dbcontext.session.add(test)
                    fail = BuildFails(build_id=build_number, test_name=test_name)
                    dbcontext.session.add(fail)

            if found > 9:
                break

        last_update = Settings.query.filter_by(name='last_update').first()
        if last_update is None:
            last_update = Settings(name='last_update', value=str(datetime.now))
            dbcontext.session.add(last_update)
        else:
            last_update.value = str(datetime.now())

        dbcontext.session.commit()
        return f'Added {count} new builds'

    return app