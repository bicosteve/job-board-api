from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime


class DateOrOngoing(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if value == 'ongoing':
            return value
        try:
            return datetime.strptime(value, '%d-%m-%Y').date()
        except ValueError:
            raise ValidationError(
                'Must be `ongoing` or date in dd-MM-YYYY format')


class EducationSchema(Schema):
    level = fields.Str(
        required=True,
        allvalidate=validate.OneOf(
            ['Secondary', 'University', 'Certificates'])
    )
    institution = fields.Str(
        required=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={'error': 'This field is required'}
    )
    field = fields.Str(required=False, allow_none=True)
    start_date = fields.Date(required=True, format='%d-%m-%Y')
    end_date = DateOrOngoing(required=True)
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=2, max=500)],
        error_messages={
            'error': 'This field is required and must be between 2 and 500 characters'}
    )
