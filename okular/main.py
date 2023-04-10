import html
import jenkinsapi

from datetime import datetime
from flask import Flask
from jenkinsapi.jenkins import Jenkins
from okular import db
from okular.parser import Parser
from okular.models import Builds, BuildFails, Tests

def create_app(jenkins_api, jenkins_job):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okular.sqlite3'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        builds_html = f''

        builds = Builds.query.order_by(Builds.id.desc()).all()
        for build in builds:
            fails = f''
            for fail in build.fails:
                fails = f'{fails}<p class="test">{fail.name}</p>'
            builds_html = f'{builds_html}<div class="build-container"><h4>{build.date} <a href="{build.url}">{build.id}</a>: {build.status}</h4><p class="title">{build.name}</p>{fails}</div>'

        style = '<style>.build-container { margin: 10px; padding: 10px; border: solid 1px silver; }</style>'
        return f'<html><head>{style}</head><body><p>Watching: {jenkins_api}, {jenkins_job}</p>{builds_html}</body></html>'

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

                build = Builds(id=build_number, status=status, name=name, url=url, date=date)
                db.session.add(build)
                count = count + 1

                console = html.escape(jenkins_build.get_console())
                parser = Parser(console)
                parser.parse()
                fails = parser.get_fails()

                for test_name in fails:
                    test = Tests.query.filter_by(name=test_name).first()
                    if test is None:
                        test = Tests(name=test_name)
                        db.session.add(test)
                    fail = BuildFails(build_id=build_number, test_name=test_name)
                    db.session.add(fail)

            if found > 9:
                break
        db.session.commit()
        return f'Added {count} new builds'

    return app