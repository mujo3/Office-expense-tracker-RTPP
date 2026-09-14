def test_login_success(client, test_user):
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'You have been logged in.' in response.data

def test_login_invalid_password(client, test_user):
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b'Invalid email or password.' in response.data

def test_login_nonexistent_user(client):
    response = client.post('/login', data={
        'email': 'nouser@example.com',
        'password': 'irrelevant'
    }, follow_redirects=True)

    assert b'Invalid email or password.' in response.data


def test_login_required_fields(client):


    response = client.post('/login', data={
        'email': '',
        'password': ''
    }, follow_redirects=True)

    assert (
        b'This field is required' in response.data or
        b'Polje je obavezno' in response.data or
        b'Invalid email or password' in response.data
    )

def test_login_missing_email(client):


    response = client.post('/login', data={
        'email': '',
        'password': 'somepassword'
    }, follow_redirects=True)

    assert (
        b'This field is required' in response.data or
        b'Polje je obavezno' in response.data or
        b'Invalid email or password' in response.data
    )


def test_login_missing_password(client):


    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': ''
    }, follow_redirects=True)

    assert (
        b'This field is required' in response.data or
        b'Polje je obavezno' in response.data or
        b'Invalid email or password' in response.data
    )

