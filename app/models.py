from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'type': self.type,
            'category': self.category,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        
        
# class Transaction(db.Model):

# This creates a database table called transactions
# Every class that extends db.Model becomes a table in your database

# python__tablename__ = 'transactions'

# Sets the actual table name in database

# pythonid = db.Column(db.Integer, primary_key=True)

# Creates an ID column that auto increments
# primary_key=True means every row has a unique ID

# pythontitle = db.Column(db.String(100), nullable=False)

# Creates a title column
# nullable=False means this field is required — can't be empty

# pythoncategory = db.Column(db.String(50), nullable=True)

# Category is optional — can be empty

# pythondef to_dict(self):

# This converts a Transaction object to a dictionary
# So we can easily return it as JSON in our API


