from marshmallow import (Schema, ValidationError, fields, validate,
                         validates_schema)


class SocialSchema(Schema):
    """Social schema."""

    email = fields.Email()
    fan_page = fields.URL()
    instagram = fields.Str()
    line = fields.Str()
    telephone = fields.Str()
    website = fields.URL()
    youtube = fields.URL()


class CreateOrgSchema(Schema):
    """POST:create_org."""

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

    description = fields.Str()
    address = fields.Str()
    social = fields.Nested(SocialSchema)


class CreateEventSchema(Schema):
    """POST:create_event."""

    name = fields.Str(required=True)
    description = fields.Str()
    address = fields.Str()
    amount = fields.Int(required=True, validate=validate.Range(min=0))
    end_at = fields.TimeDelta(required=True)
    price = fields.Int(required=True, validate=validate.Range(min=0))
    reg_end_at = fields.TimeDelta(required=True)
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta(required=True)
    start_at = fields.TimeDelta(required=True)

    social = fields.Nested(SocialSchema)


class UpdateEventSchema(Schema):
    """PUT:update_event."""

    name = fields.Str()
    description = fields.Str()
    address = fields.Str()
    amount = fields.Int(validate=validate.Range(min=0))
    end_at = fields.TimeDelta()
    price = fields.Int(validate=validate.Range(min=0))
    reg_end_at = fields.TimeDelta()
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    start_at = fields.TimeDelta()

    social = fields.Nested(SocialSchema)
