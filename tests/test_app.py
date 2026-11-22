import io
import json
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

import pytest

import app as weather_app


@pytest.fixture
def client():
    return weather_app.app.test_client()


def test_home_displays_search_form_without_calling_weather_service(client, monkeypatch):
    def unexpected_request(*args, **kwargs):
        pytest.fail('The homepage must not fetch weather before a search')
    monkeypatch.setattr(weather_app, 'urlopen', unexpected_request, raising=False)
    response = client.get('/')
    assert response.status_code == 200
    assert b'Weather' in response.data
    assert b'name="city"' in response.data
    assert b'Open-Meteo' in response.data


def test_city_search_displays_weather_and_location(client, monkeypatch):
    calls = []
    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        if len(calls) == 1:
            data = {'results': [{'name': 'Springfield', 'admin1': 'Illinois', 'country': 'United States', 'latitude': 39.8, 'longitude': -89.6}]}
        else:
            data = {'current': {'temperature_2m': 72.5, 'relative_humidity_2m': 60, 'wind_speed_10m': 9.3, 'weather_code': 3}, 'current_units': {'temperature_2m': '\u00b0F', 'wind_speed_10m': 'mph'}}
        return io.BytesIO(json.dumps(data).encode())
    monkeypatch.setattr(weather_app, 'urlopen', fake_urlopen, raising=False)
    response = client.get('/', query_string={'city': 'Springfield'})
    assert response.status_code == 200
    assert b'Springfield' in response.data and b'Illinois' in response.data
    assert b'72.5' in response.data and b'60%' in response.data and b'9.3' in response.data
    assert b'Overcast' in response.data
    assert len(calls) == 2
    assert parse_qs(urlparse(calls[0][0]).query)['name'] == ['Springfield']
    assert parse_qs(urlparse(calls[1][0]).query)['latitude'] == ['39.8']
    assert all(0 < timeout <= 10 for _, timeout in calls)


def test_unknown_city_displays_helpful_message(client, monkeypatch):
    monkeypatch.setattr(weather_app, 'urlopen', lambda *a, **k: io.BytesIO(b'{}'), raising=False)
    response = client.get('/', query_string={'city': 'DefinitelyNotACity'})
    assert b'No locations found' in response.data


def test_blank_or_overlong_city_does_not_call_api(client, monkeypatch):
    def unexpected_request(*args, **kwargs):
        pytest.fail('Invalid input must not call the API')
    monkeypatch.setattr(weather_app, 'urlopen', unexpected_request, raising=False)
    for city in (' ', 'x' * 101):
        response = client.get('/', query_string={'city': city})
        assert b'Enter a city' in response.data


@pytest.mark.parametrize('failure', [URLError('offline'), TimeoutError(), ValueError('invalid JSON')])
def test_service_failure_shows_error(client, monkeypatch, failure):
    def broken(*args, **kwargs):
        raise failure
    monkeypatch.setattr(weather_app, 'urlopen', broken, raising=False)
    response = client.get('/', query_string={'city': 'Boston'})
    assert b'Weather service is unavailable' in response.data


def test_city_input_is_html_escaped(client, monkeypatch):
    monkeypatch.setattr(weather_app, 'urlopen', lambda *a, **k: io.BytesIO(b'{}'), raising=False)
    response = client.get('/', query_string={'city': '<script>alert(1)</script>'})
    assert b'<script>' not in response.data
    assert b'&lt;script&gt;' in response.data


def test_health_returns_json_without_external_service(client, monkeypatch):
    def unexpected_request(*args, **kwargs):
        pytest.fail('Health must not depend on the weather service')
    monkeypatch.setattr(weather_app, 'urlopen', unexpected_request, raising=False)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'healthy'}
