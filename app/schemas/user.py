from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class RegisterSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=1, error="Email cannot be empty"),
            validate.Email(),
        ],
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, error="Password cannot be empty"),
        ],
        error_messages={"required": "Password field is required"},
    )
    confirm_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, error="Confirm password cannot be empty"),
        ],
        error_messages={"required": "Confirm password field is required"},
    )

    @validates_schema
    def validate_password_match(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError(
                {
                    "confirm_password": ["Passwords do not match"],
                }
            )


class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=1, error="Email cannot be empty"),
            validate.Email(),
        ],
        error_messages={"required": "Email field is required"},
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, error="Password cannot be empty"),
        ],
        error_messages={"required": "Password field is required"},
    )


class VerifyAccountSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=1, error="Email cannot be empty"),
            validate.Email(),
        ],
        error_messages={"required": "Email field is required"},
    )
    verification_code = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, error="Verification code cannot be empty"),
        ],
        error_messages={"required": "Verification code field is required"},
    )
