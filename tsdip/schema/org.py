from marshmallow import (Schema, ValidationError, fields, validate,
                         validates_schema)


class CreateOrgSchema(Schema):
    """POST:create_org."""

    class SocialSchema(Schema):
        email = fields.Email()
        fan_page = fields.URL()
        instagram = fields.Str()
        line = fields.Str()
        telephone = fields.Str()
        website = fields.URL()
        youtube = fields.URL()

    name = fields.Str(required=True)
    description = fields.Str()
    address = fields.Str()
    org_type = fields.Str(
        required=True,
        validate=validate.OneOf(['dance_group', 'studio'])
    )
    social = fields.Nested(SocialSchema)


class InviteMemberSchema(Schema):
    """POST:invite_member."""

    email = fields.Email()
    user_id = fields.Str()

    @validates_schema
    def validate_filed(self, data, **kwargs):
        """Customize validation function."""
        if 'email' not in data and 'user_id' not in data:
            raise ValidationError('At least one fields: email or user_id')


class UpdateOrgSchema(Schema):
    """POST:update_org."""

    class SocialSchema(Schema):
        email = fields.Email()
        fan_page = fields.URL()
        instagram = fields.Str()
        line = fields.Str()
        telephone = fields.Str()
        website = fields.URL()
        youtube = fields.URL()

    description = fields.Str()
    address = fields.Str()
    social = fields.Nested(SocialSchema)
