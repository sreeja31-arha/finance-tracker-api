# app/auth.py

import logging  # ← Python's built-in logging module
from flask import Blueprint, jsonify, request
from app import db
from app.models import User
from app.schemas import RegisterSchema, LoginSchema
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

# Creates a logger named "app.auth" (from __name__)
# This is safer than current_app.logger — works outside request context too
# Writes to the same handlers configured in logging_config.py
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # DEBUG: track what's coming in — useful when debugging bad requests
    # NEVER log the password — even at DEBUG level
    logger.debug(
        "Register attempt — email: %s",
        data.get('email') if data else 'NO BODY'
    )

    try:
        validated_data = register_schema.load(data)
    except ValidationError as err:
        # WARNING: expected failure — user sent bad data, not a system crash
        logger.warning("Register validation failed: %s", err.messages)
        return jsonify({'errors': err.messages}), 400

    if User.query.filter_by(email=validated_data['email']).first():
        # WARNING: expected failure — duplicate registration attempt
        logger.warning(
            "Register blocked — email already exists: %s",
            validated_data['email']
        )
        return jsonify({'message': 'Email already exists!'}), 400

    if User.query.filter_by(username=validated_data['username']).first():
        # WARNING: expected failure — duplicate username
        logger.warning(
            "Register blocked — username already taken: %s",
            validated_data['username']
        )
        return jsonify({'message': 'Username already exists!'}), 400

    hashed_password = generate_password_hash(validated_data['password'])
    user = User(
        username=validated_data['username'],
        email=validated_data['email'],
        password=hashed_password
    )

    # Wrap DB operations in try/except
    # If commit fails: rollback undoes the broken transaction so the
    # DB session stays clean for future requests
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # ERROR: unexpected system failure
        # exc_info=True attaches the full traceback to the log file
        logger.error(
            "DB error during register for %s: %s",
            validated_data['email'], e,
            exc_info=True
        )
        return jsonify({'message': 'Registration failed due to a server error.'}), 500

    # INFO: one clean success line per registration
    logger.info(
        "New user registered — id: %s, email: %s",
        user.id, validated_data['email']
    )
    return jsonify({
        'message': 'User registered successfully!',
        'user': user.to_dict()
    }), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # DEBUG: track login attempts — never log the password
    logger.debug(
        "Login attempt — email: %s",
        data.get('email') if data else 'NO BODY'
    )

    try:
        validated_data = login_schema.load(data)
    except ValidationError as err:
        logger.warning("Login validation failed: %s", err.messages)
        return jsonify({'errors': err.messages}), 400

    user = User.query.filter_by(email=validated_data['email']).first()

    if not user or not check_password_hash(user.password, validated_data['password']):
        # WARNING: wrong credentials — expected failure
        # We don't say "user not found" vs "wrong password" — that would leak
        # which emails are registered (a security vulnerability)
        logger.warning(
            "Failed login attempt — email: %s",
            validated_data['email']
        )
        return jsonify({'message': 'Invalid email or password!'}), 401

    access_token = create_access_token(identity=str(user.id))

    # INFO: successful login — who logged in and when
    logger.info(
        "User logged in — id: %s, email: %s",
        user.id, validated_data['email']
    )
    return jsonify({
        'message': 'Login successful!',
        'access_token': access_token,
        'user': user.to_dict()
    })