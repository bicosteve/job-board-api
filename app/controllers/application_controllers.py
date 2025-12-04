from flask_restful import Resource, request
from marshmallow import ValidationError
from flasgger import swag_from

from ..schemas.application import (
    JobApplicationSchema,
    JobUpdateSchema,
    ApplicationIdSchema,
    JobPaginaNationSchema

)
from ..services.application_service import ApplicationService
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


class ApplicationsListController(Resource):
    @swag_from('../docs/get_jobs.yml')
    def get(self):
        schema = JobPaginaNationSchema()
        try:
            args = schema.load(request.args)
            if not isinstance(args, dict):
                Logger.warn(f'Error with the args dict {args}')
                return {'error': 'Bad request'}, 400

            page_number = args['page']
            limit = args['limit']
            job_id = args['job_id']

            if limit < 10:
                limit = 5

            if page_number < 1:
                page_number = 1

            if job_id < 1:
                job_id = 1

            result = ApplicationService.get_all_job_applications(job_id,
                                                                 page_number, limit)
            return {'result': result}, 200
        except Exception as e:
            return {'error': str(e)}, 400
