from marshmallow import Schema, fields


class ManagerSignUpSchema(Schema):
    email = fields.Email(required=True)
    telephone = fields.Str()
    username = fields.Str(required=True)
