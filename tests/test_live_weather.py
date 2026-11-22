"""Optional end-to-end test requiring the deployment and the live weather API."""
from urllib.parse import urlencode
from urllib.request import urlopen

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.live_weather]


def test_deployed_city_search_returns_live_weather():
    url = 'http://127.0.0.1:8080/?' + urlencode({'city': 'Boston, United States'})
    with urlopen(url, timeout=20) as response:
        body = response.read().decode('utf-8')
        assert response.status == 200
        assert 'class="result"' in body, 'Weather result missing; check Open-Meteo availability.'
        assert 'Boston, Massachusetts, United States' in body
        assert 'Humidity' in body and 'Wind' in body
        print('Live search returned current weather for Boston, Massachusetts, United States.')
