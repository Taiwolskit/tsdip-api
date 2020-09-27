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
    """POST:create_organization."""

    name = fields.Str(required=True)
    org_type = fields.Str(
        required=True,
        validate=validate.OneOf(['dance_group', 'studio'])
    )
    description = fields.Str()
    social = fields.Nested(SocialSchema)


class GetOrgsSchema(Schema):
    """GET:get_organizations."""

    page = fields.Int(validate=validate.Range(min=1))
    limit = fields.Int(validate=validate.Range(min=1, max=50))
    org_type = fields.Str(
        validate=validate.OneOf(['dance_group', 'studio'])
    )


class UpdateOrgSchema(Schema):
    """POST:update_organization."""

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
    start_at = fields.TimeDelta()
    end_at = fields.TimeDelta()
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    reg_end_at = fields.TimeDelta()

    social = fields.Nested(SocialSchema)
    tickets = fields.List(fields.Nested(TicketSchema))
