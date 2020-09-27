from marshmallow import Schema, fields, validate


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


class UpdateEventSchema(Schema):
    """PUT:update_event."""

    name = fields.Str()
    description = fields.Str()
    start_at = fields.TimeDelta()
    end_at = fields.TimeDelta()
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    reg_end_at = fields.TimeDelta()


class UpdateTicketSchema(Schema):
    """PUT:update_event_tickets."""

    id = fields.UUID(required=True)
    name = fields.Str()
    description = fields.Str()
    amount = fields.Int(validate=validate.Range(min=0))
    price = fields.Int(validate=validate.Range(min=0))
    reg_link = fields.URL()
    reg_start_at = fields.TimeDelta()
    reg_end_at = fields.TimeDelta()
