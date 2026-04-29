# tests/test_auth.py
#
# These tests cover your /api/v1/auth/register and /api/v1/auth/login endpoints.
# Every function that starts with test_ is automatically found and run by pytest.


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_register_success(client):
    """
    WHAT: Send a valid registration request
    EXPECT: 201 status code + success message
    WHY: This is the happy path — everything correct, should work perfectly
    """
    response = client.post('/api/v1/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Check the status code
    assert response.status_code == 201
    # assert means "I am claiming this is true"
    # If response.status_code is NOT 201, this test fails and pytest
    # shows you exactly which line failed and what value it got instead

    # Check the response body
    data = response.get_json()
    # response.get_json() converts the JSON response into a Python dictionary

    assert data['message'] == 'User registered successfully!'
    # Check the message is correct

    assert 'user' in data
    # Check that a 'user' key exists in the response
    # We don't check exact values here — just that the key exists


def test_register_duplicate_email(client):
    """
    WHAT: Register the same email twice
    EXPECT: 400 on the second attempt
    WHY: Your app should reject duplicate emails
    """
    # First registration — should succeed
    client.post('/api/v1/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Second registration with SAME email — should fail
    response = client.post('/api/v1/auth/register', json={
        'username': 'john2',         # different username
        'email': 'john@example.com', # same email ← this should cause 400
        'password': 'password123'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Email already exists!'


def test_register_duplicate_username(client):
    """
    WHAT: Register the same username twice
    EXPECT: 400 on the second attempt
    WHY: Your app should reject duplicate usernames
    """
    # First registration
    client.post('/api/v1/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Second registration with SAME username
    response = client.post('/api/v1/auth/register', json={
        'username': 'john',           # same username ← this should cause 400
        'email': 'john2@example.com', # different email
        'password': 'password123'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Username already exists!'


def test_register_missing_fields(client):
    """
    WHAT: Send registration with missing required fields
    EXPECT: 400 status code
    WHY: Your marshmallow schema should reject incomplete data
    """
    # Send request with no body at all
    response = client.post('/api/v1/auth/register', json={})

    assert response.status_code == 400
    # We don't check the exact error message here because marshmallow
    # generates it automatically and the format might change


def test_register_missing_password(client):
    """
    WHAT: Send registration without a password
    EXPECT: 400 status code
    WHY: Password is a required field in your schema
    """
    response = client.post('/api/v1/auth/register', json={
        'username': 'john',
        'email': 'john@example.com'
        # password is missing
    })

    assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_login_success(client):
    """
    WHAT: Register a user then login with correct credentials
    EXPECT: 200 status code + access_token in response
    WHY: Happy path — correct credentials should return a JWT token
    """
    # First register a user — we need someone to log in as
    client.post('/api/v1/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Now login
    response = client.post('/api/v1/auth/login', json={
        'email': 'john@example.com',
        'password': 'password123'
    })

    assert response.status_code == 200

    data = response.get_json()
    assert data['message'] == 'Login successful!'
    assert 'access_token' in data
    # The most important check — did we get a token back?
    # Without a token, the user can't access protected endpoints

    assert data['access_token'] is not None
    # Make sure the token isn't empty


def test_login_wrong_password(client):
    """
    WHAT: Login with correct email but wrong password
    EXPECT: 401 status code
    WHY: Wrong credentials should be rejected
    """
    # Register first
    client.post('/api/v1/auth/register', json={
        'username': 'john',
        'email': 'john@example.com',
        'password': 'password123'
    })

    # Login with wrong password
    response = client.post('/api/v1/auth/login', json={
        'email': 'john@example.com',
        'password': 'wrongpassword'  # ← wrong password
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Invalid email or password!'


def test_login_nonexistent_user(client):
    """
    WHAT: Login with an email that was never registered
    EXPECT: 401 status code
    WHY: Non-existent users should be rejected
    Note: We return the same message as wrong password on purpose —
    we don't want to reveal which emails are registered (security)
    """
    response = client.post('/api/v1/auth/login', json={
        'email': 'nobody@example.com',  # never registered
        'password': 'password123'
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Invalid email or password!'


def test_login_missing_fields(client):
    """
    WHAT: Login with empty body
    EXPECT: 400 status code
    WHY: Missing fields should be caught by marshmallow schema validation
    """
    response = client.post('/api/v1/auth/login', json={})

    assert response.status_code == 400