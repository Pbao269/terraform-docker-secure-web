"""Run after terraform apply: pytest tests/test_deployment.py."""
import json
import subprocess
from urllib.request import urlopen

import pytest

pytestmark = pytest.mark.integration


def test_health_is_proxied_with_security_header():
    with urlopen('http://127.0.0.1:8080/health', timeout=5) as response:
        assert response.status == 200
        assert json.load(response) == {'status': 'healthy'}
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_only_proxy_has_a_published_port_and_both_share_network():
    data = subprocess.check_output(
        ['docker', 'inspect', 'secure-web-proxy', 'secure-web-app'], text=True
    )
    proxy, app = json.loads(data)
    assert proxy['HostConfig']['PortBindings']['80/tcp'][0]['HostIp'] == '127.0.0.1'
    assert proxy['HostConfig']['PortBindings']['80/tcp'][0]['HostPort'] == '8080'
    assert not app['HostConfig']['PortBindings']
    assert 'secure-web-network' in proxy['NetworkSettings']['Networks']
    assert 'secure-web-network' in app['NetworkSettings']['Networks']


def test_weather_search_page_is_served_through_proxy():
    with urlopen('http://127.0.0.1:8080/', timeout=5) as response:
        body = response.read()
        assert response.status == 200
        assert b'Weather, wherever' in body
        assert b'name="city"' in body
        assert b'Open-Meteo' in body
