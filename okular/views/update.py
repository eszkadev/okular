import flask
import html
import time
import requests
from datetime import datetime
from flask import Blueprint

from okular import dbcontext
from okular.db.models import Builds, BuildFails, Settings, Tests
from okular.parser import Parser

update_blueprint = Blueprint("update", __name__, template_folder='templates')

@update_blueprint.route('/update')
def update():
    if len(flask.current_app.config['JENKINS_API']) == 0:
        return "Bad configuration: missing API URL"
    if len(flask.current_app.config['JENKINS_JOB']) == 0:
        return "Bad configuration: missing JOB"

    api_url = flask.current_app.config['JENKINS_API'].rstrip('/')
    job_name = flask.current_app.config['JENKINS_JOB']
    job_url = '%s/job/%s' % (api_url, job_name)

    # Hit the job's own REST endpoints directly instead of going through the
    # jenkinsapi client, which polls <root>/api/python (the whole list of jobs
    # on the server) just to reach one job. The `tree` filter trims each
    # response to the fields we store, and the {0,10} range fetches only the
    # 10 newest builds rather than the full history.
    session = requests.Session()
    resp = session.get(
        '%s/api/json' % job_url,
        params={'tree': 'builds[number,url]{0,10}'},
    )
    resp.raise_for_status()
    builds = resp.json().get('builds', [])

    count = 0
    found = 0
    for build_info in builds:
        found = found + 1
        build_number = build_info['number']
        url = build_info['url']
        build = Builds.query.filter_by(id=build_number).first()
        if build is None:
            meta = session.get(
                '%s/%s/api/json' % (job_url, build_number),
                params={'tree': 'result,description,timestamp'},
            )
            meta.raise_for_status()
            meta = meta.json()

            status = meta.get('result')
            name = meta.get('description')
            # Match jenkinsapi's get_timestamp(): a naive UTC datetime built
            # from the Java epoch-milliseconds value.
            date = datetime(*time.gmtime(meta['timestamp'] / 1000.0)[:6])

            if status is None:
                continue

            console_resp = session.get('%s/%s/consoleText' % (job_url, build_number))
            console_resp.raise_for_status()
            console = html.escape(console_resp.text)
            parser = Parser(console)
            parser.parse()
            fails = parser.get_fails()

            build = Builds(
                id=build_number,
                status=status,
                name=name,
                url=url,
                date=date,
                gerrit_url=parser.get_gerrit_url(),
                gerrit_change_number=parser.get_gerrit_change_number(),
                gerrit_subject=parser.get_gerrit_subject(),
            )
            dbcontext.session.add(build)
            count = count + 1

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