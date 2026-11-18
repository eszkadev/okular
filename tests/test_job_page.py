from datetime import datetime
import pytest

from okular import dbcontext
from okular.db.models import Builds
from okular.main import create_app


def add_build(build_id, **fields):
    dbcontext.session.add(Builds(id=build_id, status='FAILURE',
                                 url='https://jenkins.example/job/job/%d/' % build_id,
                                 date=datetime(2026, 11, 5, 10, 0), **fields))


@pytest.fixture
def client():
    app = create_app('https://jenkins.example', 'job', database_uri='sqlite://')
    with app.app_context():
        add_build(1, name='<b>Fix</b> & <i>tidy</i>')
        add_build(2, gerrit_url='https://gerrit.example/c/online/+/1234', gerrit_change_number='1234',
                  gerrit_subject='calc: fix paste of wide text')
        add_build(3, gerrit_url='ftp://gerrit.example/5678', gerrit_change_number='5678',
                  gerrit_subject='writer: keep tabs')
        dbcontext.session.commit()
        yield app.test_client()


def test_build_description_is_shown_as_text(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '&lt;b&gt;Fix&lt;/b&gt; &amp; &lt;i&gt;tidy&lt;/i&gt;' in html
    assert '<b>Fix</b>' not in html


def test_change_number_links_to_gerrit(client):
    html = client.get('/').get_data(as_text=True)
    assert '<a href="https://gerrit.example/c/online/+/1234">1234</a>: calc: fix paste of wide text' in html


def test_change_link_only_for_web_addresses(client):
    html = client.get('/').get_data(as_text=True)
    assert 'ftp://gerrit.example/5678' not in html
    assert '<a href="https://jenkins.example/job/job/3/">3</a>: writer: keep tabs' in html
