

# class Config:
#     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/finance_tracker'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = 'finance-tracker-secret-key'
    
    
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:123456@localhost:5432/finance_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'finance-tracker-secret-key'
    
    
        
# SQLALCHEMY_DATABASE_URI

# This is the connection string to your PostgreSQL database
# Format is: postgresql://username:password@host:port/database_name
# Replace admin123 with whatever password you set in pgAdmin=123456


# SQLALCHEMY_TRACK_MODIFICATIONS = False

# Turns off a Flask-SQLAlchemy feature we don't need
# Saves memory and avoids warnings