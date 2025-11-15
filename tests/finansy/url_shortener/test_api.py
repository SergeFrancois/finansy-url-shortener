import pytest
import requests
import sqlite3
from urllib.parse import urljoin, urlparse
from .constants import BASE_API_URL, BASE_URL, DB_URL, URL_TO_SHORTEN


def row_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@pytest.fixture
def get_db_connection():
    connection = sqlite3.connect(DB_URL, check_same_thread=False)
    connection.row_factory = row_factory
    return connection


class TestApi:
    
    state = {}
    
    @pytest.mark.dependency
    def test_shorten_url_creation(self, get_db_connection):
        response = requests.post(
            urljoin(BASE_API_URL, 'shorten'),
            json={'url': URL_TO_SHORTEN}
        ).json()
        shorten_url = urlparse(response['shorten_url'])
        code = shorten_url.path.rsplit('/', 1)[1]
        with get_db_connection as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('select * from shorten_url as su where su.code = ?', (code,))
            shorten_url = cursor.fetchone()
        assert URL_TO_SHORTEN == shorten_url['original_url']
        assert shorten_url['request_count'] == 0
        self.state['shorten_url_code'] = code
    
    @pytest.mark.dependency(depends=['TestApi::test_shorten_url_creation'])
    def test_url_redirect(self, get_db_connection):
        code = self.state['shorten_url_code']
        response = requests.get(urljoin(BASE_URL, f'/s/{code}'))
        assert response.status_code == 200
    
    @pytest.mark.dependency(depends=['TestApi::test_url_redirect'])
    def test_shorten_url_statistics_getting(self, get_db_connection):
        code = self.state['shorten_url_code']
        requests.get(urljoin(BASE_API_URL, f'/stats/{code}'))
        with get_db_connection as db_connection:
            cursor = db_connection.cursor()
            cursor.execute('select * from shorten_url as su where su.code = ?', (code,))
            shorten_url = cursor.fetchone()
        assert shorten_url['request_count'] == 1
