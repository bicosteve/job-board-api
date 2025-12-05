from flask_restful import Resource, request
from marshmallow import ValidationError
from flasgger import swag_from

from ..schemas.job import (
    JobSchema,
    PaginationSchema,
    JobIdSchema,
    JobUpdateSchema
)
from ..services.job_service import JobService
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


class PostJobController(Resource):

    @swag_from('../docs/create_job.yml')
    def post(self):
        try:
            token_or_error = get_auth_token()

            # Check if flask returns a tuple or dict
            # this is how flask return errors
            if isinstance(token_or_error, tuple):
                return token_or_error

            # if it is a string assign token_or_error to token
            token = token_or_error

            job_schema = JobSchema()
            payload = job_schema.load(request.get_json())

            if not isinstance(payload, dict):
                return {'validation_err': f"payload {payload} has an error"}, 400

            details = payload['details']

            data = {
                "title": payload['title'],
                "description": details['description'],
                "token": token,
                ** payload['details']
            }

            row_id = JobService.add_job(data)
            if not row_id:
                return {'error': 'An error occurred while inserting job'}, 500

            data['job_id'] = row_id

            return {'msg': 'job created', 'data': job_schema.dump(data)}, 201
        except ValidationError as e:
            return {'validation_err': str(e)}, 400


class JobsListController(Resource):

    @swag_from('../docs/get_jobs.yml')
    def get(self):

        try:
            schema = PaginationSchema()
            args = schema.load(request.args)
            if not isinstance(args, dict):
                Logger.warn(f'Error with the args dict {args}')
                return {'error': 'Bad request'}, 400

            page_number = args['page']
            limit = args['limit']

            if limit < 10:
                limit = 5

            if page_number < 1:
                page_number = 1

            result = JobService.fetch_jobs(page_number, limit)
            return {'result': result}, 200
        except Exception as e:
            return {'error': str(e)}, 400


class JobObjectController(Resource):
    @swag_from("../docs/get_job.yml")
    def get(self, job_id):
        schema = JobIdSchema()
        try:
            validated = schema.load({'job_id': job_id})
            if not isinstance(validated, dict):
                return {'errors': f'error with {job_id}'}, 400
            job = JobService.fetch_job(int(validated['job_id']))
            if not job:
                return {'message': 'Job not found'}, 404
            return job, 200
        except ValidationError as err:
            return {'errors': f'error because of {str(err.messages)}'}, 400
        except Exception as e:
            return {'error': str(e)}, 400


class ModifyJobObjectController(Resource):
    @swag_from("../docs/update_job.yml")
    def put(self, job_id):
        update_schema = JobUpdateSchema()
        id_schema = JobIdSchema()
        try:
            payload = update_schema.load(request.get_json())
            if not isinstance(payload, dict):
                return {'error': 'invalid payload'}, 400

            validated = id_schema.load({'job_id': job_id})
            if not isinstance(validated, dict):
                return {'error': 'invalid payload'}, 400

            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                return token_or_error

            id = int(validated['job_id'])
            token = token_or_error

            data = {
                **payload
            }

            job = JobService.update_job(id, token, data)
            if not job:
                return {'msg': 'error job not found'}, 401
            return job, 200
        except ValidationError as err:
            return {'errors': f'error due to {str(err.messages)}'}, 400
        except Exception as e:
            return {'error': str(e)}, 400
