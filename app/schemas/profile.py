from marshmallow import Schema, fields, validate


class ProfileSchema(Schema):
    first_name = fields.Str(
        required=True,
        validate=[validate.Length(min=2, max=100)],
        error_messages={
            'error': 'required and must be between 2 and 100 characters'}
    )
    last_name = fields.Str(
        required=True,
        validate=[validate.Length(min=2, max=100)],
        error_messages={
            'error': 'required and must be between 2 and 100 characters'}
    )
    cv_url = fields.Str(required=False, allow_none=True)
