from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError
)


class RegisterAdminSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=1, error="Email cannot be empty"),
            validate.Email()
        ]
    )

    password = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=1, max=20, error="password must be between 1-20 characters")
        ],
        error_messages={"error": "Password cannot be empty"}
    )

    confirm_password = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=1, max=20, error="Confirm password must be between 1-20 characters")
        ],
        error_messages={"error": "Confirm password cannot be empty"}
    )

    @validates_schema
    def validate_password_match(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError({"error": "Passwords do not match"})


class LoginAdminSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=1, error="Email cannot be empty"),
            validate.Email()
        ]
    )

    password = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=1, max=20, error="password must be between 1-20 characters")
        ],
        error_messages={"error": "Password cannot be empty"}
    )


class VerifyAdminSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[
            validate.Email()
        ],
        error_message="Email field is required"
    )

    verification_code = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, error="code must be 6 characters")
        ],
        error_message="verification code is required"
    )
