from flask_restful import Resource, request
from marshmallow import ValidationError
from flasgger import swag_from


from ..schemas.education import EducationSchema
from ..utils.logger import Logger
from ..services.education_service import EducationService
from ..utils.exceptions import (
    GenericDatabaseError,
    GenericGenerateAuthTokenError
)

# Helpers


def get_auth_token():
    '''Extract and validate the Bearer token from Authrization header'''
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        Logger.warn('No authorizatio token in the header')
        return {'validation_err': 'Unauthorized'}, 401

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    else:
        return {'error': 'Invalid auth header format'}, 401


class EducationController(Resource):

    @swag_from("../docs/create_education.yml")
    def post(self):
        try:
            schema = EducationSchema()
            Logger.info('validating education payload')
            payload = schema.load(request.get_json())
            if not isinstance(payload, dict):
                Logger.warn(f'Payload error: expected object got {payload}')
                return {'msg': 'Payload error: expected object got list or None'}, 400

            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                return {'error': f'{token_or_error}'}, 400

            token = token_or_error

            row_count = EducationService.create_education(token, payload)
            if row_count < 1:
                return {'error': f'Failed to create education for {payload}'}, 500

            return {'msg': 'Education created'}, 201
        except ValidationError as err:
            return {'error': f'{str(err.messages)}'}, 400
        except GenericGenerateAuthTokenError as e:
            return {'error': f'{str(e)}'}, 400
        except GenericDatabaseError as e:
            return {'error': f'{str(e)}'}, 500
