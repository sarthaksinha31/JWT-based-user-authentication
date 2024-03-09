'''Marshmallow schema to validate request and response of the certain endpoints'''
from marshmallow import fields, Schema, ValidationError, validates
import re


class UserSchema(Schema):
    id = fields.String()
    email = fields.String()

class RegistrationSchema(Schema):
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    description = fields.Str(required=False)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

    @validates("password")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', value):
            raise ValidationError("Password must contain at least one uppercase character.")

        if not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one digit.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character.")

