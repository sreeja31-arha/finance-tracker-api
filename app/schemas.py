from marshmallow import Schema, fields, validate, ValidationError

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class TransactionSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    type = fields.Str(required=True, validate=validate.OneOf(['income', 'expense']))
    category = fields.Str(load_default=None)
    
    
    
    
# fields.Str(required=True, validate=validate.Length(min=3, max=50))

# Field must be a string
# Required means it cannot be empty
# Length must be between 3 and 50 characters

# pythonfields.Email(required=True)

# Validates proper email format like john@gmail.com
# Rejects john or john@ automatically

# pythonfields.Float(required=True, validate=validate.Range(min=0.01))

# Amount must be a number
# Must be at least 0.01 — can't add zero or negative amount

# pythonvalidate.OneOf(['income', 'expense'])

# Type must be exactly income or expense
# Rejects anything else like salary or cost