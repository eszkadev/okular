import html
import jenkinsapi

from datetime import datetime
from flask import Flask
from jenkinsapi.jenkins import Jenkins
from okular import db
from okular.parser import Parser
from okular.models import Builds, BuildFails, Settings, Tests

def create_app(jenkins_api, jenkins_job):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okular.sqlite3'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        builds_html = f''

        last_update = Settings.query.filter_by(name='last_update').first()
        last_update_str = '-'
        if not last_update is None:
            last_update_str = last_update.value

        builds = Builds.query.order_by(Builds.id.desc()).limit(15).all()
        for build in builds:
            fails = f''
            for fail in build.fails:
                fails = f'{fails}<li class="list-group-item">{fail.name}</li>'

            status_class = ''
            if build.status == 'SUCCESS':
                status_class = 'bg-success text-light'
            elif build.status == 'FAILURE':
                status_class = 'bg-danger text-light'

            builds_html = f'{builds_html}<div class="card" style="width: 95%; margin: 10px auto;"><h4 class="card-header {status_class}"><a href="{build.url}">{build.id}</a>: {build.name}</h4><div class="card-body"><p>{build.date} {build.status}</p><ul class="list-group list-group-flush">{fails}</ul></div></div>'

        style = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">'
        navbar = f'<nav class="navbar navbar-expand-lg navbar-light bg-light"><div class="container-fluid"><span class="nav-item">{jenkins_api}</span><span class="nav-item">Last update: {last_update_str}</span><span class="nav-item">Job: {jenkins_job}</span></div></nav>'
        return f'<html><head>{style}</head><body>{navbar}{builds_html}</body></html>'

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

        last_update = Settings.query.filter_by(name='last_update').first()
        if last_update is None:
            last_update = Settings(name='last_update', value=str(datetime.now))
            db.session.add(last_update)
        else:
            last_update.value = str(datetime.now())

        db.session.commit()
        return f'Added {count} new builds'

    return app