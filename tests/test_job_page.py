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
        dbcontext.session.commit()
        yield app.test_client()


def test_build_description_is_shown_as_text(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '&lt;b&gt;Fix&lt;/b&gt; &amp; &lt;i&gt;tidy&lt;/i&gt;' in html
    assert '<b>Fix</b>' not in html
