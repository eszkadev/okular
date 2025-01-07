import flask
import html
from datetime import datetime
from flask import Blueprint
from jenkinsapi.jenkins import Jenkins

from okular import dbcontext

from okular.db.models import Builds, BuildFails, Settings, Tests
from okular.parser import Parser
from okular.views.base import BaseView

update_blueprint = Blueprint("update", __name__, template_folder='templates')

class UpdateView(BaseView):
    def __init__(self, base_view_model):
        super().__init__(base_view_model)

@update_blueprint.route('/update')
def update():
    if len(flask.current_app.config['JENKINS_API']) == 0:
        return "Bad configuration: missing API URL"
    if len(flask.current_app.config['JENKINS_JOB']) == 0:
        return "Bad configuration: missing JOB"

    j = Jenkins(flask.current_app.config['JENKINS_API'])
    job = j[flask.current_app.config['JENKINS_JOB']]
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

            if status is None:
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