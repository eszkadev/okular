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


def samples(body, metric):
    """Map label string to value for every sample of one metric."""
    found = {}
    for line in body.splitlines():
        if line.startswith(metric + '{'):
            labels, value = line[len(metric):].rsplit(' ', 1)
            found[labels] = value
    return found


def test_returns_every_failing_test_for_the_day(client):
    response = client.get('/api/job/job/dashboard?date=2026-11-05')
    assert response.status_code == 200
    assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
    body = response.get_data(as_text=True)

    day = '{jenkins_job="job",date="2026-11-05"}'
    assert samples(body, 'okular_day_builds') == {day: '14'}
    assert samples(body, 'okular_day_failed_builds') == {day: '13'}
    assert samples(body, 'okular_day_success_rate_percent') == {day: '7'}
    assert '# TYPE okular_day_test_failures gauge' in body

    failures = samples(body, 'okular_day_test_failures')
    assert len(failures) == 12
    assert failures['{jenkins_job="job",date="2026-11-05",test="test_00"}'] == '2'
    assert failures['{jenkins_job="job",date="2026-11-05",test="test_01"}'] == '2'
    assert 'other_day' not in body
    # Every test name is written once and the list is ordered by count, descending.
    names = [line.split('test="')[1].split('"')[0]
             for line in body.splitlines() if line.startswith('okular_day_test_failures{')]
    assert names[:2] == ['test_00', 'test_01']
    assert sorted(names[2:]) == names[2:]


def test_day_without_builds(client):
    body = client.get('/api/job/job/dashboard?date=2026-01-01').get_data(as_text=True)
    day = '{jenkins_job="job",date="2026-01-01"}'
    assert samples(body, 'okular_day_builds') == {day: '0'}
    assert samples(body, 'okular_day_failed_builds') == {day: '0'}
    # Without builds there is no rate to report, so the metric has no sample.
    assert samples(body, 'okular_day_success_rate_percent') == {}
    assert samples(body, 'okular_day_test_failures') == {}


def test_label_values_are_escaped(client):
    app = client.application
    with app.app_context():
        add_build(400, datetime(2026, 11, 7, 1, 0), ['quote"back\\slash'])
        dbcontext.session.commit()
    body = client.get('/api/job/job/dashboard?date=2026-11-07').get_data(as_text=True)
    assert 'test="quote\\"back\\\\slash"' in body


def test_invalid_date(client):
    response = client.get('/api/job/job/dashboard?date=yesterday')
    assert response.status_code == 400
    assert 'Invalid date' in response.get_data(as_text=True)


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
