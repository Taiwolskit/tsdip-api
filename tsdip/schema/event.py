from marshmallow import Schema, fields, validate


class SocialSchema(Schema):
    """Social schema."""

    email = fields.Email()
    fan_page = fields.URL()
    instagram = fields.Str()
    line = fields.Str()
    telephone = fields.Str()
    website = fields.URL()
    youtube = fields.URL()


class CreateEventSchema(Schema):
    """POST:create_event."""

    org_id = fields.UUID(required=True)

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
