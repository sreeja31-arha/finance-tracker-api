# tests/test_transactions.py
#
# These tests cover all your transaction endpoints.
# Notice these tests use 'auth_client' instead of 'client' —
# because all transaction endpoints require a JWT token.


# ═══════════════════════════════════════════════════════════════════════════════
# PROTECTION TESTS — verify endpoints reject unauthenticated requests
# ═══════════════════════════════════════════════════════════════════════════════

def test_add_transaction_without_token(client):
    """
    WHAT: Try to add a transaction without a JWT token
    EXPECT: 401 status code
    WHY: @jwt_required() should block unauthenticated requests
    Note: Uses 'client' (not auth_client) — we intentionally send no token
    """
    response = client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000,
        'type': 'income'
    })

    assert response.status_code == 401


def test_get_transactions_without_token(client):
    """
    WHAT: Try to get transactions without a JWT token
    EXPECT: 401 status code
    WHY: @jwt_required() protects GET endpoint too
    """
    response = client.get('/api/v1/transactions')
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# ADD TRANSACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_add_transaction_success(auth_client):
    """
    WHAT: Add a valid transaction as a logged-in user
    EXPECT: 201 status code + transaction data in response
    WHY: Happy path — valid data + valid token should create transaction
    Note: Uses 'auth_client' — automatically sends JWT token with request
    """
    response = auth_client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000.00,
        'type': 'income',
        'category': 'work'
    })

    assert response.status_code == 201

    data = response.get_json()
    assert data['message'] == 'Transaction added successfully!'
    assert 'transaction' in data

    # Check the transaction data matches what we sent
    transaction = data['transaction']
    assert transaction['title'] == 'Salary'
    assert transaction['amount'] == 5000.00
    assert transaction['type'] == 'income'
    assert transaction['category'] == 'work'


def test_add_transaction_missing_fields(auth_client):
    """
    WHAT: Add a transaction with missing required fields
    EXPECT: 400 status code
    WHY: Marshmallow schema should reject incomplete data
    """
    response = auth_client.post('/api/v1/transactions', json={
        'title': 'Salary'
        # amount and type are missing
    })

    assert response.status_code == 400


def test_add_transaction_without_category(auth_client):
    """
    WHAT: Add a transaction without a category (category is optional)
    EXPECT: 201 status code
    WHY: Category is nullable in your model so this should succeed
    """
    response = auth_client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000.00,
        'type': 'income'
        # no category — that's fine, it's optional
    })

    assert response.status_code == 201


# ═══════════════════════════════════════════════════════════════════════════════
# GET TRANSACTIONS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_get_transactions_empty(auth_client):
    """
    WHAT: Get transactions when none have been added yet
    EXPECT: 200 status code + empty list
    WHY: Should return empty list, not crash
    """
    response = auth_client.get('/api/v1/transactions')

    assert response.status_code == 200

    data = response.get_json()
    assert 'transactions' in data
    assert data['transactions'] == []
    # Empty list — no transactions added yet


def test_get_transactions_returns_correct_data(auth_client):
    """
    WHAT: Add 2 transactions then fetch them
    EXPECT: 200 status code + list with exactly 2 transactions
    WHY: Should return only THIS user's transactions
    """
    # Add first transaction
    auth_client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000.00,
        'type': 'income'
    })

    # Add second transaction
    auth_client.post('/api/v1/transactions', json={
        'title': 'Rent',
        'amount': 1500.00,
        'type': 'expense',
        'category': 'housing'
    })

    # Now fetch all transactions
    response = auth_client.get('/api/v1/transactions')

    assert response.status_code == 200

    data = response.get_json()
    assert len(data['transactions']) == 2
    # We added exactly 2, we should get exactly 2 back


# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE TRANSACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_update_transaction_success(auth_client):
    """
    WHAT: Create a transaction then update its title and amount
    EXPECT: 200 status code + updated values in response
    WHY: Valid update with correct token should work
    """
    # First create a transaction
    create_response = auth_client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000.00,
        'type': 'income'
    })
    transaction_id = create_response.get_json()['transaction']['id']
    # Get the ID from the created transaction so we can update it

    # Now update it
    response = auth_client.put(f'/api/v1/transactions/{transaction_id}', json={
        'title': 'Updated Salary',
        'amount': 6000.00
    })

    assert response.status_code == 200

    data = response.get_json()
    assert data['transaction']['title'] == 'Updated Salary'
    assert data['transaction']['amount'] == 6000.00


def test_update_nonexistent_transaction(auth_client):
    """
    WHAT: Try to update a transaction ID that doesn't exist
    EXPECT: 404 status code
    WHY: Should return not found, not crash
    """
    response = auth_client.put('/api/v1/transactions/99999', json={
        'title': 'Ghost Transaction'
    })

    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Transaction not found!'


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE TRANSACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_delete_transaction_success(auth_client):
    """
    WHAT: Create a transaction then delete it
    EXPECT: 200 status code + success message
    WHY: Valid delete with correct token should work
    """
    # First create a transaction
    create_response = auth_client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000.00,
        'type': 'income'
    })
    transaction_id = create_response.get_json()['transaction']['id']

    # Now delete it
    response = auth_client.delete(f'/api/v1/transactions/{transaction_id}')

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Transaction deleted successfully!'


def test_delete_nonexistent_transaction(auth_client):
    """
    WHAT: Try to delete a transaction ID that doesn't exist
    EXPECT: 404 status code
    WHY: Should return not found, not crash
    """
    response = auth_client.delete('/api/v1/transactions/99999')

    assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def test_analytics_correct_calculation(auth_client):
    """
    WHAT: Add known transactions then check analytics math
    EXPECT: 200 + correct totals
    WHY: Analytics endpoint should correctly sum income and expenses
    """
    # Add income: 5000
    auth_client.post('/api/v1/transactions', json={
        'title': 'Salary',
        'amount': 5000.00,
        'type': 'income'
    })

    # Add expense: 1500
    auth_client.post('/api/v1/transactions', json={
        'title': 'Rent',
        'amount': 1500.00,
        'type': 'expense',
        'category': 'housing'
    })

    # Add another expense: 500
    auth_client.post('/api/v1/transactions', json={
        'title': 'Groceries',
        'amount': 500.00,
        'type': 'expense',
        'category': 'food'
    })

    response = auth_client.get('/api/v1/transactions/analytics')

    assert response.status_code == 200

    data = response.get_json()
    assert data['total_income'] == 5000.00
    assert data['total_expense'] == 2000.00    # 1500 + 500
    assert data['net_balance'] == 3000.00      # 5000 - 2000

    # Check categories breakdown
    assert data['categories']['housing'] == 1500.00
    assert data['categories']['food'] == 500.00