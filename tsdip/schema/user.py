from marshmallow import Schema, ValidationError, fields, validates_schema


class UserSignUpSchema(Schema):
    """POST:sign_up."""

    email = fields.Email(required=True)
    telephone = fields.Str()
    username = fields.Str(required=True)


class InviteMemberSchema(Schema):
    """POST:invite_member."""

    email = fields.Email()
    user_id = fields.Str()

    @validates_schema
    def validate_filed(self, data, **kwargs):
        """Customize validation function."""
        if 'email' not in data and 'user_id' not in data:
            raise ValidationError('At least one fields: email or user_id')
