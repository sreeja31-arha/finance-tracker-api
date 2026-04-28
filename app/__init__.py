from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes import main
    from app.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'Resource not found!'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'message': 'Method not allowed!'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'message': 'Internal server error!'}), 500

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'message': 'Missing or invalid token!'}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired! Please login again.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({'message': 'Invalid token!'}), 401

    return app




# db = SQLAlchemy()

# Creates SQLAlchemy instance — this is our database connection

# pythondef create_app():

# This is called Application Factory Pattern
# Instead of creating app directly we use a function
# This is the proper professional way to structure Flask apps

# pythonapp.config.from_object(Config)

# Loads our config settings into the app

# pythondb.init_app(app)

# Connects our database to the app

# pythonapp.register_blueprint(main)

# Registers our routes — we will create these next