import re
from datetime import datetime
import pytest

from okular import dbcontext
from okular.db.models import Builds, BuildFails, Tests
from okular.main import create_app


def add_build(build_id, when, fails):
    dbcontext.session.add(Builds(id=build_id, status='FAILURE' if fails else 'SUCCESS',
                                 name='build %d' % build_id, url='', date=when))
    for test_name in fails:
        if Tests.query.filter_by(name=test_name).first() is None:
            dbcontext.session.add(Tests(name=test_name))
        dbcontext.session.add(BuildFails(build_id=build_id, test_name=test_name))


@pytest.fixture
def client():
    app = create_app('https://jenkins.example', 'job', database_uri='sqlite://')
    with app.app_context():
        # Twelve distinct failing tests on 2026-11-05, more than the dashboard's top 10.
        for i in range(12):
            add_build(100 + i, datetime(2026, 11, 5, 10, i), ['test_%02d' % i])
        add_build(200, datetime(2026, 11, 5, 23, 59, 59), ['test_00', 'test_01'])
        add_build(201, datetime(2026, 11, 5, 12, 0), [])
        # Neighbouring days must not leak in.
        add_build(300, datetime(2026, 11, 4, 23, 59, 59), ['other_day'])
        add_build(301, datetime(2026, 11, 6, 0, 0, 0), ['other_day'])
        dbcontext.session.commit()
        yield app.test_client()


def test_returns_every_failing_test_for_the_day(client):
    response = client.get('/api/job/job/dashboard?date=2026-11-05')
    assert response.status_code == 200
    body = response.get_json()

    assert body['job'] == 'job'
    assert body['date'] == '2026-11-05'
    assert body['builds_count'] == 14
    assert body['build_fails_count'] == 13
    assert body['success_rate'] == 7

    assert len(body['fails']) == 12
    assert body['fails'][0] == {'test_name': 'test_00', 'count': 2}
    assert body['fails'][1] == {'test_name': 'test_01', 'count': 2}
    assert all(fail['count'] == 1 for fail in body['fails'][2:])
    assert 'other_day' not in [fail['test_name'] for fail in body['fails']]


def test_day_without_builds(client):
    body = client.get('/api/job/job/dashboard?date=2026-01-01').get_json()
    assert body == {'job': 'job', 'date': '2026-01-01', 'builds_count': 0,
                    'build_fails_count': 0, 'success_rate': None, 'fails': []}


def test_invalid_date(client):
    response = client.get('/api/job/job/dashboard?date=yesterday')
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_dashboard_page_keeps_top_ten(client):
    from unittest.mock import patch
    import okular.viewmodels.job_dashboard as vm

    class FakeDate(vm.date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 6)

    with patch.object(vm, 'date', FakeDate):
        response = client.get('/job/job/dashboard')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    rows = re.findall(r'<td>([^<]+)</td>\s*<td>(\d+)</td>', html)
    assert len(rows) == 10
    assert rows[0] == ('other_day', '2')
