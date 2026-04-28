from flask import Blueprint, jsonify, request
from app import db
from app.models import User
from app.schemas import RegisterSchema, LoginSchema
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

auth = Blueprint('auth', __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()

@auth.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate input
    try:
        validated_data = register_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    # Check if user already exists
    if User.query.filter_by(email=validated_data['email']).first():
        return jsonify({'message': 'Email already exists!'}), 400

    if User.query.filter_by(username=validated_data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 400

    # Create new user
    hashed_password = generate_password_hash(validated_data['password'])

    user = User(
        username=validated_data['username'],
        email=validated_data['email'],
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully!',
        'user': user.to_dict()
    }), 201


@auth.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate input
    try:
        validated_data = login_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    # Find user by email
    user = User.query.filter_by(email=validated_data['email']).first()

    # Check if user exists and password is correct
    if not user or not check_password_hash(user.password, validated_data['password']):
        return jsonify({'message': 'Invalid email or password!'}), 401

    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful!',
        'access_token': access_token,
        'user': user.to_dict()
    })