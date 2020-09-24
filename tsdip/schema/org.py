from marshmallow import (Schema, ValidationError, fields, validate,
                         validates_schema)


class SocialSchema(Schema):
    """Social schema."""

    address = fields.Str()
    email = fields.Email()
    fan_page = fields.URL()
    instagram = fields.Str()
    line = fields.Str()
    telephone = fields.Str()
    website = fields.URL()
    youtube = fields.URL()


class TicketSchema(Schema):
    """Ticket fare schema."""

    name = fields.Str(required=True)
    description = fields.Str()
    amount = fields.Int(required=True, validate=validate.Range(min=0))
    price = fields.Int(required=True, validate=validate.Range(min=0))
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    reg_end_at = fields.TimeDelta()


class CreateOrgSchema(Schema):
    """POST:create_org."""

    name = fields.Str(required=True)
    org_type = fields.Str(
        required=True,
        validate=validate.OneOf(['dance_group', 'studio'])
    )
    description = fields.Str()
    social = fields.Nested(SocialSchema)


class UpdateOrgSchema(Schema):
    """POST:update_org."""

    description = fields.Str()
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


class CreateEventSchema(Schema):
    """POST:create_event."""

    name = fields.Str(required=True)
    description = fields.Str()
    address = fields.Str()
    start_at = fields.TimeDelta()
    end_at = fields.TimeDelta()
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    reg_end_at = fields.TimeDelta()

    social = fields.Nested(SocialSchema)
    tickets = fields.List(fields.Nested(TicketSchema))


class UpdateEventSchema(Schema):
    """PUT:update_event."""

    name = fields.Str()
    description = fields.Str()
    address = fields.Str()
    start_at = fields.TimeDelta()
    end_at = fields.TimeDelta()
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    reg_end_at = fields.TimeDelta()

    social = fields.Nested(SocialSchema)
