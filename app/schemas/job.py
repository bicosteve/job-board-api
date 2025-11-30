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
            ['Full time', 'Part time', 'Contract', 'Internship'])
    )
    salary_range = fields.String(
        allow_none=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={"length_error": "Must be between 3 and 100 characters"}
    )
    deadline = fields.Date(allow_none=True)
    status = fields.String(
        required=True,
        validate=validate.OneOf(['Open', 'Closed', 'Draft'])
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


class PaginationSchema(Schema):
    page = fields.Int(
        missing=1,
        validate=validate.Range(min=1),
        error_messages={'invalid': 'Page must be positive integer'}
    )
    limit = fields.Int(
        missing=10,
        validate=validate.Range(min=1, max=100),
        error_messages={'invalid': 'Limit must be between 1 and 100'}
    )


class JobIdSchema(Schema):
    job_id = fields.Int(required=True)


class JobUpdateSchema(Schema):
    title = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=100)],
        error_messages={"length_error": "Must be between 1 and 100 characters"}
    )
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
            ['Full time', 'Part time', 'Contract', 'Internship'])
    )
    salary_range = fields.String(
        allow_none=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={"length_error": "Must be between 3 and 100 characters"}
    )
    deadline = fields.Date(allow_none=True)
    status = fields.String(
        required=True,
        validate=validate.OneOf(['Open', 'Closed', 'Draft'])
    )
    company_name = fields.String(
        required=True,
        validate=[validate.Length(min=3, max=100)],
        error_messages={"length_error": "Must be between 3 and 100 characters"}

    )
    application_url = fields.Url(allow_none=True)
