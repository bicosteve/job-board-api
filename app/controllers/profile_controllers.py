from flask_restful import Resource, request
from marshmallow import ValidationError
from flasgger import swag_from

from ..schemas.profile import ProfileSchema

from ..services.profile_service import ProfileService
from ..utils.logger import Logger
from ..utils.exceptions import GenericDatabaseError


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


class ProfileCreateController(Resource):

    @swag_from("../docs/create_profile.yml")
    def post(self):
        try:
            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                return token_or_error

            token = token_or_error

            schema = ProfileSchema()
            payload = schema.load(request.get_json())

            if not isinstance(payload, dict):
                return {'error': f'Error validating payload {payload}'}, 400

            row_count = ProfileService.create_profile(token, payload)
            if row_count < 1:
                Logger.warn('User profile was not created')
                return {'error': 'User profile was not created'}, 500

            return {'msg': 'Profile created'}, 201
        except ValidationError as e:
            return {'err'f'{(str(e.messages))}'}, 400
        except Exception as e:
            return {'error': str(e)}, 400


class ProfileGetController(Resource):
    @swag_from("../docs/get_profile.yml")
    def get(self):

        try:
            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                return token_or_error

            token = token_or_error

            profile = ProfileService.get_profile(token)
            if not profile:
                return {'error': 'Profile not found'}, 404

            return {'profile': profile}, 200
        except GenericDatabaseError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': str(e)}, 400
