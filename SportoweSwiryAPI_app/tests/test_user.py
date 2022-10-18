import pytest

def test_create_user(client):
    response = client.post('/api/v1/users',
                            json={
                                'name': 'test',
                                'last_name': 'Test',
                                'mail': 'test@wp.pl',
                                'password': '12345678'
                            })
    response_data = response.get_json()
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['token']

@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'last_name': 'test', 'mail': 'test@wp.pl', 'password': '12345678'}, 'name'),
        ({'name': 'test', 'mail': 'test@wp.pl', 'password': '12345678'}, 'last_name'),
        ({'name': 'test', 'last_name': 'Test', 'password': '12345678'}, 'mail'),
        ({'name': 'test', 'last_name': 'Test', 'mail': 'test@wp.pl'}, 'password')
    ]
)
def test_create_user_invalid_data(client, data, missing_field):
    response = client.post('/api/v1/users',
                            json=data)
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_create_user_invalid_content_type(client):
    response = client.post('/api/v1/users',
                            data={
                                'name': 'test',
                                'last_name': 'Test',
                                'mail': 'test@wp.pl',
                                'password': '12345678'
                            })
    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_create_user_already_used_mail(client, user):
    response = client.post('/api/v1/users',
                            json={
                                'name': 'test',
                                'last_name': 'Test',
                                'mail': user['mail'],
                                'password': '12345678'
                            })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_login_user(client, user):
    response = client.post('/api/v1/login',
                            json={
                                'mail': user['mail'],
                                'password': user['password']
                            })
    response_data = response.get_json()
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert 'token' in response_data


def test_login_user_invalid_password(client, user):
    response = client.post('/api/v1/login',
                            json={
                                'mail': user['mail'],
                                'password': 'wrong_password'
                            })
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert 'mail' not in response_data
    assert 'name' not in response_data
    assert 'last_name' not in response_data
    assert 'Invalid credentials' in response_data['message']


def test_login_user_invalid_mail(client, user):
    response = client.post('/api/v1/login',
                            json={
                                'mail': 'wrong_mail',
                                'password': user['password']
                            })
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert 'mail' not in response_data
    assert 'name' not in response_data
    assert 'last_name' not in response_data
    assert 'Invalid credentials' in response_data['message']


def test_login_user_invalid_credentials(client):
    response = client.post('/api/v1/login',
                            json={
                                'mail': 'wrong_mail',
                                'password': 'wrong_password'
                            })
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert 'mail' not in response_data
    assert 'name' not in response_data
    assert 'last_name' not in response_data
    assert 'Invalid credentials' in response_data['message']
    

@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'mail': 'test@wp.pl'}, 'password'),
        ({'password': '12345678'}, 'mail')
    ]
)
def test_login_user_missing_data(client, data, missing_field):
    response = client.post('/api/v1/login',
                            json=data)
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_get_current_user(client, user, token):
    response = client.get('/api/v1/me',
                            headers={
                                'Authorization': f'Bearer {token}'
                            })
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['name'] == user['name']
    assert response_data['last_name'] == user['last_name']
    assert response_data['mail'] == user['mail']


def test_get_current_user_missing_token(client):
    response = client.get('/api/v1/me')
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'name' not in response_data
    assert 'last_name' not in response_data
    assert 'mail' not in response_data


def test_update_password(client, user, token):
    response = client.put('/api/v1/update/password',
			                headers={
                                'Authorization': f'Bearer {token}'
                            },
                            json={
                                'current_password': user['password'],
                                'new_password': 'new_password'
                            })
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert user['mail'] in response_data['data'].values()
    assert user['name'] in response_data['data'].values()
    assert user['last_name'] in response_data['data'].values()


def test_update_password_missing_token(client, user):
    response = client.put('/api/v1/update/password',
                            json={
                                'current_password': user['password'],
                                'new_password': 'new_password'
                            })
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert user['mail'] not in response_data
    assert user['name'] not in response_data
    assert user['last_name'] not in response_data


def test_update_password_invalid_current_password(client, token):
    response = client.put('/api/v1/update/password',
			                headers={
                                'Authorization': f'Bearer {token}'
                            },
                            json={
                                'current_password': 'wrong_password',
                                'new_password': 'new_password'
                            })
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert 'mail' not in response_data
    assert 'name' not in response_data
    assert 'last_name' not in response_data
    assert 'Invalid credentials' in response_data['message']


@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'current_password': '12345678'}, 'new_password'),
        ({'new_password': 'new_password'}, 'current_password')
    ]
)
def test_update_password_missing_data(client, token, data, missing_field):
    response = client.put('/api/v1/update/password',
			                headers={
                                'Authorization': f'Bearer {token}'
                            },
                            json=data)
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert 'mail' not in response_data
    assert 'name' not in response_data
    assert 'last_name' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]