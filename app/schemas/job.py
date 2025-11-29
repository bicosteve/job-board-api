from marshmallow import Schema, fields, validate


class JobDetailsSchema(Schema):
    description = fields.String(
        required=True,
        validate=[validate.Length(min=3, max=1000)],
        error_messages={"field": "This field is required"})
    requirements = fields.String(allow_none=True)
    location = fields.String(
        required=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={"length_error": "Must be between 3 and 100 characters"}
    )
    employment_type = fields.String(
        required=True,
        validate=validate.OneOf(
            ['full time', 'part time', 'contract', 'internship'])
    )
    salary_range = fields.String(
        allow_none=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={"length_error": "Must be between 3 and 100 characters"}
    )
    deadline = fields.Date(allow_none=True)
    status = fields.String(
        required=True,
        validate=validate.OneOf(['open', 'closed', 'draft'])
    )
    company_name = fields.String(
        required=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={"length_error": "Must be between 3 and 100 characters"}

    )
    application_url = fields.Url(allow_none=True)


class JobSchema(Schema):
    title = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=100)],
        error_messages={"length_error": "Must be between 1 and 100 characters"}
    )
    details = fields.Nested(JobDetailsSchema)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
