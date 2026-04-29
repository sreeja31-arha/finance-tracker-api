# tests/conftest.py
#
# conftest.py is a special file that pytest reads automatically.
# All fixtures defined here are available to every test file
# without needing to import them.

import pytest
from app import create_app, db


# ── Fixture 1: app ────────────────────────────────────────────────────────────
# This creates a fresh Flask app configured specifically for testing.
# The 'scope="function"' means a brand new app is created for EVERY test.
# This ensures tests never affect each other.
@pytest.fixture(scope='function')
def app():
    app = create_app()

    # Override config for testing:
    app.config['TESTING'] = True
    # TESTING=True → Flask shows real error messages instead of generic 500 pages
    # This makes it much easier to debug when a test fails

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # sqlite:///:memory: → creates a temporary database in RAM
    # Why SQLite instead of PostgreSQL?
    #   - No setup needed — it just works
    #   - Lives in memory — created fresh, destroyed after each test
    #   - Your real PostgreSQL data is NEVER touched by tests

    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    # Use a fixed secret key for tests so JWT tokens are predictable

    app.config['WTF_CSRF_ENABLED'] = False
    # Disable CSRF protection in tests — we're not testing forms

    # Create all tables in the test database before the test runs
    with app.app_context():
        db.create_all()
        # db.create_all() reads your models.py and creates the tables
        # in the SQLite in-memory database

    yield app
    # yield hands the app to the test
    # Everything ABOVE yield = setup (runs before test)
    # Everything BELOW yield = teardown (runs after test)

    # Drop all tables after each test so the next test starts clean
    with app.app_context():
        db.drop_all()
        # db.drop_all() deletes every table
        # This means each test starts with a completely empty database
        # No leftover users or transactions from previous tests


# ── Fixture 2: client ─────────────────────────────────────────────────────────
# This gives every test a fake browser to send HTTP requests with.
# It depends on the 'app' fixture above — pytest automatically runs
# the app fixture first, then passes it here.
@pytest.fixture
def client(app):
    return app.test_client()
    # app.test_client() is Flask's built-in fake browser
    # You can call .post(), .get(), .put(), .delete() on it
    # Just like Postman but in Python code


# ── Fixture 3: auth_client ────────────────────────────────────────────────────
# Some endpoints require a JWT token (like adding transactions).
# This fixture:
#   1. Registers a test user
#   2. Logs in and gets the JWT token
#   3. Returns a client that automatically sends the token with every request
#
# Any test that needs a logged-in user uses 'auth_client' instead of 'client'
@pytest.fixture
def auth_client(client):
    # Step 1: Register a test user
    client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # We don't assert here because this is just setup, not the actual test

    # Step 2: Login and capture the response
    login_response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })

    # Step 3: Extract the JWT token from the response
    token = login_response.get_json()['access_token']
    # login_response.get_json() → converts the JSON response to a Python dict
    # ['access_token'] → gets the token string from that dict

    # Step 4: Create a special client class that sends the token automatically
    # Without this, every test would have to manually add the Authorization header
    class AuthenticatedClient:
        """
        A wrapper around Flask's test client that automatically adds
        the Authorization header to every request.
        This simulates a logged-in user making requests.
        """
        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {token}'
            return client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {token}'
            return client.post(*args, **kwargs)

        def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {token}'
            return client.put(*args, **kwargs)

        def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {token}'
            return client.delete(*args, **kwargs)

    return AuthenticatedClient()
    # Now any test using auth_client gets a client that behaves like
    # a logged-in user — no need to manually add tokens in every test