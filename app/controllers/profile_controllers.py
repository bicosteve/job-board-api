from flask_restful import Resource, request
from marshmallow import ValidationError
from flasgger import swag_from

from ..schemas.profile import (
    ProfileSchema
)
from ..services.profile_service import ProfileService
from ..utils.logger import Logger


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


class ProfileController(Resource):
    def post(self):
        pass
