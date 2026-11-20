from app import app


def test_home_returns_application_page():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert b'Secure Web Application' in response.data


def test_health_returns_json_status():
    response = app.test_client().get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'healthy'}
