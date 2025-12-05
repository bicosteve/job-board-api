from marshmallow import Schema, fields, validate


class JobPaginaNationSchema(Schema):
    job_id = fields.Int(
        required=True,
        default=1,
        validate=[validate.Range(min=1)],
        error_messages={
            'required': 'This field is required',
            'invalid': 'Must be an integer',
            'min': 'Must be 1 or above'
        }

    )
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1),
        error_messages={'required': 'Page must be positive integer'}
    )
    limit = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100),
        error_messages={'required': 'Limit must be between 1 and 100'}
    )


class JobApplicationSchema(Schema):
    job_id = fields.Int(
        required=True,
        validate=[validate.Range(min=1)],
        error_messages={
            'required': 'This field is required',
            'invalid': 'Must be an integer',
            'min': 'Must be 1 or above'
        }

    )
    status = fields.Int(
        required=True,
        allvalidate=validate.OneOf([1, 2, 3, 4]),
        error_messages={
            'required': 'This field is required',
            'invalid': 'Must be an integer',
            'range': 'Must be between 1 and 4'
        }
    )
    cover_letter = fields.Str(required=False, allow_none=True)
    resume_url = fields.Str(required=False, allow_none=True)


class JobUpdateSchema(Schema):
    status = fields.Int(
        required=True,
        validate=validate.OneOf([1, 2, 3, 4]),
        error_messages={
            'required': 'This field is required',
            'invalid': 'Must be an integer',
            'range': 'Must be between 1 and 4'
        }
    )


class ApplicationIdSchema(Schema):
    application_id = fields.Int(
        required=True,
        validate=[validate.Range(min=1)],
        error_messages={
            'required': 'This field is required',
            'invalid': 'Must be an integer',
            'min': 'Must be 1 or above'
        }
    )
