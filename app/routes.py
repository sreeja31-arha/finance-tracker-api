# app/routes.py

import logging  # ← Python's built-in logging module
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Transaction
from app.schemas import TransactionSchema
from marshmallow import ValidationError

# Creates a logger named "app.routes" (from __name__)
# Separate from "app.auth" — so in your log file you can tell which
# file each message came from
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

transaction_schema = TransactionSchema()


@main.route('/')
def home():
    # DEBUG: lightweight health check trace — only visible in log file
    logger.debug("Health check endpoint hit")
    return jsonify({
        'message': 'Welcome to Finance Tracker API!',
        'status': 'running'
    })


@main.route('/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # DEBUG: log what the user is trying to create
    logger.debug(
        "Add transaction request — user_id: %s, data: %s",
        current_user_id, data
    )

    try:
        validated_data = transaction_schema.load(data)
    except ValidationError as err:
        # WARNING: user sent invalid data — their mistake, not a system error
        logger.warning(
            "Transaction validation failed — user_id: %s, errors: %s",
            current_user_id, err.messages
        )
        return jsonify({'errors': err.messages}), 400

    transaction = Transaction(
        title=validated_data['title'],
        amount=validated_data['amount'],
        type=validated_data['type'],
        category=validated_data.get('category', None),
        user_id=current_user_id
    )

    # Wrap DB write in try/except
    # rollback() on failure keeps the DB session clean for future requests
    try:
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # ERROR: unexpected DB failure — exc_info=True adds full traceback
        logger.error(
            "DB error saving transaction — user_id: %s: %s",
            current_user_id, e,
            exc_info=True
        )
        return jsonify({'message': 'Failed to save transaction.'}), 500

    # INFO: one clean line confirming what was created and by whom
    logger.info(
        "Transaction created — id: %s, type: %s, amount: %s, user_id: %s",
        transaction.id, transaction.type, transaction.amount, current_user_id
    )
    return jsonify({
        'message': 'Transaction added successfully!',
        'transaction': transaction.to_dict()
    }), 201


@main.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()

    # ── Step 1: Read query parameters from the URL ────────────────────────
    # request.args reads everything after ? in the URL
    # Example: /transactions?page=2&limit=10&type=expense&category=food

    page = request.args.get('page', 1, type=int)
    # 'page' → parameter name
    # 1      → default value if not provided
    # type=int → automatically converts "2" string to 2 integer
    # If user doesn't send ?page=... we default to page 1

    limit = request.args.get('limit', 10, type=int)
    # How many transactions per page — default 10
    # User can override: ?limit=20

    # Filtering parameters — these are optional, default is None
    type_filter = request.args.get('type', None)
    # ?type=expense or ?type=income
    # Named type_filter because 'type' is a reserved Python keyword

    category_filter = request.args.get('category', None)
    # ?category=food

    month_filter = request.args.get('month', None)
    # ?month=2024-01 → only January 2024 transactions

    # ── Step 2: Build the query with filters ──────────────────────────────
    # Start with base query — always filter by current user first
    # We use query instead of directly calling .all() so we can
    # keep adding conditions before executing
    query = Transaction.query.filter_by(user_id=current_user_id)

    # Add type filter only if user provided it
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
        # This adds: AND type = 'expense' to the SQL query

    # Add category filter only if user provided it
    if category_filter:
        query = query.filter(Transaction.category == category_filter)
        # This adds: AND category = 'food' to the SQL query

    # Add month filter only if user provided it
    if month_filter:
        # month_filter comes in as "2024-01" (year-month string)
        # We extract year and month from it to filter by date
        try:
            year, month = month_filter.split('-')
            # split('-') turns "2024-01" into ["2024", "01"]
            # year = "2024", month = "01"

            from sqlalchemy import extract
            # extract() lets us pull year/month out of a DateTime column

            query = query.filter(
                extract('year', Transaction.created_at) == int(year),
                extract('month', Transaction.created_at) == int(month)
            )
            # This adds: AND YEAR(created_at) = 2024 AND MONTH(created_at) = 1
        except ValueError:
            # If month_filter format is wrong (not "YYYY-MM"), ignore it
            # We don't crash — we just skip the month filter silently
            logger.warning(
                "Invalid month filter format: %s — expected YYYY-MM",
                month_filter
            )

    # ── Step 3: Get total count BEFORE pagination ─────────────────────────
    # We need total_items to calculate total_pages
    # .count() runs: SELECT COUNT(*) with all our filters applied
    # We do this BEFORE .offset() and .limit() so we count ALL matching
    # records, not just the current page
    total_items = query.count()

    # Calculate total pages
    # math.ceil rounds UP — if we have 45 items and limit=10:
    # 45/10 = 4.5 → ceil → 5 pages
    import math
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1

    # ── Step 4: Apply pagination ──────────────────────────────────────────
    # offset() → skip records from previous pages
    # limit()  → take only this page's records
    # .all()   → execute the query and return results
    transactions = query.offset((page - 1) * limit).limit(limit).all()
    # page 1: offset(0).limit(10)  → records 1-10
    # page 2: offset(10).limit(10) → records 11-20
    # page 3: offset(20).limit(10) → records 21-30

    # ── Step 5: Log what happened ─────────────────────────────────────────
    logger.info(
        "Fetched %d transactions (page %d/%d) — user_id: %s | filters: type=%s, category=%s, month=%s",
        len(transactions), page, total_pages, current_user_id,
        type_filter, category_filter, month_filter
    )

    # ── Step 6: Return data with pagination metadata ──────────────────────
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'pagination': {
            'page': page,               # current page number
            'limit': limit,             # items per page
            'total_items': total_items, # total matching transactions
            'total_pages': total_pages, # total number of pages
            'has_next': page < total_pages,  # is there a next page?
            'has_prev': page > 1             # is there a previous page?
        },
        'filters': {
            'type': type_filter,        # echo back what filters were applied
            'category': category_filter,# helps the client know what's active
            'month': month_filter
        }
    })

@main.route('/transactions/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # DEBUG: log update intent before touching the DB
    logger.debug(
        "Update transaction request — id: %s, user_id: %s, data: %s",
        id, current_user_id, data
    )

    transaction = Transaction.query.filter_by(
        id=id, user_id=current_user_id
    ).first()

    if not transaction:
        # WARNING: could be a wrong ID or someone probing another user's data
        logger.warning(
            "Transaction not found for update — id: %s, user_id: %s",
            id, current_user_id
        )
        return jsonify({'message': 'Transaction not found!'}), 404

    try:
        validated_data = transaction_schema.load(data, partial=True)
    except ValidationError as err:
        logger.warning(
            "Update validation failed — id: %s, errors: %s",
            id, err.messages
        )
        return jsonify({'errors': err.messages}), 400

    transaction.title = validated_data.get('title', transaction.title)
    transaction.amount = validated_data.get('amount', transaction.amount)
    transaction.type = validated_data.get('type', transaction.type)
    transaction.category = validated_data.get('category', transaction.category)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(
            "DB error updating transaction — id: %s: %s",
            id, e,
            exc_info=True
        )
        return jsonify({'message': 'Failed to update transaction.'}), 500

    logger.info(
        "Transaction updated — id: %s, user_id: %s",
        id, current_user_id
    )
    return jsonify({
        'message': 'Transaction updated successfully!',
        'transaction': transaction.to_dict()
    })


@main.route('/transactions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    current_user_id = get_jwt_identity()

    logger.debug(
        "Delete transaction request — id: %s, user_id: %s",
        id, current_user_id
    )

    transaction = Transaction.query.filter_by(
        id=id, user_id=current_user_id
    ).first()

    if not transaction:
        logger.warning(
            "Transaction not found for delete — id: %s, user_id: %s",
            id, current_user_id
        )
        return jsonify({'message': 'Transaction not found!'}), 404

    try:
        db.session.delete(transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(
            "DB error deleting transaction — id: %s: %s",
            id, e,
            exc_info=True
        )
        return jsonify({'message': 'Failed to delete transaction.'}), 500

    logger.info(
        "Transaction deleted — id: %s, user_id: %s",
        id, current_user_id
    )
    return jsonify({'message': 'Transaction deleted successfully!'})


@main.route('/transactions/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    current_user_id = get_jwt_identity()

    logger.debug("Analytics request — user_id: %s", current_user_id)

    transactions = Transaction.query.filter_by(user_id=current_user_id).all()

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net_balance = total_income - total_expense

    categories = {}
    for t in transactions:
        if t.type == 'expense':
            if t.category not in categories:
                categories[t.category] = 0
            categories[t.category] += t.amount

    # INFO: log the computed summary — useful for usage patterns
    logger.info(
        "Analytics served — user_id: %s | income: %s, expense: %s, balance: %s",
        current_user_id, total_income, total_expense, net_balance
    )
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'categories': categories
    })
            
            
    
#     main = Blueprint('main', __name__)

# Blueprint is a way to organize routes
# Instead of @app.route we now use @main.route
# This is the professional way to structure Flask apps

# pythontransaction = Transaction(...)

# We are creating a Transaction object — this maps to a row in database

# pythondb.session.add(transaction)
# db.session.commit()

# db.session.add() — prepares the transaction to be saved
# db.session.commit() — actually saves it to the database
# Think of it like — add to cart then checkout

# pythonTransaction.query.all()

# Gets all transactions from database

# pythonTransaction.query.get(id)

# Gets a single transaction by ID from database

# python[t.to_dict() for t in transactions]

# This is a list comprehension — converts all transaction objects to dictionaries

# @jwt_required()

# This decorator protects the route
# If no token is sent — request is rejected with 401 error
# If token is invalid — request is rejected

# pythoncurrent_user_id = get_jwt_identity()

# Gets the user ID from the JWT token
# Remember we stored user.id in the token when logging in

# pythonTransaction.query.filter_by(user_id=current_user_id).all()

# Gets only transactions belonging to the logged in user
# Users can never see each other's transactions ✅

# transaction_schema.load(data, partial=True)

# partial=True means for UPDATE — not all fields are required
# User can update just the amount without sending title and type