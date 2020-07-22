from marshmallow import Schema, fields, validate


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
