from marshmallow import Schema, fields


class UserSignUpSchema(Schema):
    """POST:sign_up."""

    email = fields.Email(required=True)
    telephone = fields.Str()
    username = fields.Str(required=True)


class UserProfileSchema(Schema):
    """PUT:update_profile."""

    email = fields.Email()
    telephone = fields.Str()
    username = fields.Str()
