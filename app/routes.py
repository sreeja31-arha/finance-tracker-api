from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Transaction
from app.schemas import TransactionSchema
from marshmallow import ValidationError

main = Blueprint('main', __name__)

transaction_schema = TransactionSchema()

@main.route('/')
def home():
    return jsonify({
        'message': 'Welcome to Finance Tracker API!',
        'status': 'running'
    })

@main.route('/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate input
    try:
        validated_data = transaction_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    transaction = Transaction(
        title=validated_data['title'],
        amount=validated_data['amount'],
        type=validated_data['type'],
        category=validated_data.get('category', None),
        user_id=current_user_id
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        'message': 'Transaction added successfully!',
        'transaction': transaction.to_dict()
    }), 201

@main.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=current_user_id).all()
    return jsonify({
        'transactions': [t.to_dict() for t in transactions]
    })

@main.route('/transactions/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    current_user_id = get_jwt_identity()
    data = request.get_json()

    transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()

    if not transaction:
        return jsonify({'message': 'Transaction not found!'}), 404

    # Validate input
    try:
        validated_data = transaction_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    transaction.title = validated_data.get('title', transaction.title)
    transaction.amount = validated_data.get('amount', transaction.amount)
    transaction.type = validated_data.get('type', transaction.type)
    transaction.category = validated_data.get('category', transaction.category)

    db.session.commit()

    return jsonify({
        'message': 'Transaction updated successfully!',
        'transaction': transaction.to_dict()
    })

@main.route('/transactions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    current_user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()

    if not transaction:
        return jsonify({'message': 'Transaction not found!'}), 404

    db.session.delete(transaction)
    db.session.commit()

    return jsonify({
        'message': 'Transaction deleted successfully!'
    })
    
@main.route('/transactions/analytics',methods=['GET'])
@jwt_required()
def get_analytics():
    current_user_id=get_jwt_identity()
    
    transactions=Transaction.query.filter_by(user_id=current_user_id).all()
    
    total_income=sum(t.amount for t in transactions if t.type=='income')
    total_expense=sum(t.amount for t in transactions if t.type=='expense')
    net_balance=total_income-total_expense
    
    categories={}
    
    for t in transactions:
        if t.type=='expense':
            if t.category not in categories:
                categories[t.category]=0
            categories[t.category]+=t.amount
            
    return jsonify({
        'total_income':total_income,
        'total_expense':total_expense,
        'net_balance':net_balance,
        'categories':categories
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