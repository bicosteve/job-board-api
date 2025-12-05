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


class ApplicationsListController(Resource):
    @swag_from('../docs/get_jobs_applications.yml')
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
                                                                 limit, page_number)
            return {'info': result}, 200
        except Exception as e:
            return {'error': str(e)}, 400


class ApplicationsCreateController(Resource):
    @swag_from('../docs/create_application.yml')
    def post(self):
        schema = JobApplicationSchema()
        try:
            data = schema.load(request.get_json())
            if not isinstance(data, dict):
                Logger.warn(f'Error with the payload {data}')
                return {'error': 'Bad request'}, 400

            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                Logger.warn(
                    f'Error {token_or_error} getting token from header')
                return token_or_error

            token = token_or_error

            result = ApplicationService.make_application(token, data)
            Logger.info(f'Affected rows {result}')
            if not result:
                Logger.warn(
                    f'application of {token} - {data} was not successful')
                return {'error': 'application was not successfull'}, 500
            return {'msg': 'success'}, 201
        except ValidationError as e:
            Logger.warn(f'{str(e.messages)}')
            return {'error': str(e.messages)}, 400
        except GenericDatabaseError as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}
        except Exception as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}, 400


class UsersJobApplicationsController(Resource):
    @swag_from('../docs/get_user_applications.yml')
    def get(self):
        try:
            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                Logger.warn(
                    f'Error {token_or_error} getting token from header')
                return token_or_error

            token = token_or_error

            result = ApplicationService.list_users_applications(token)
            return {'applications': result}, 200
        except GenericDatabaseError as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}
        except Exception as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}, 400


class UsersJobApplicationController(Resource):
    @swag_from('../docs/get_user_application.yml')
    def get(self, application_id):
        schema = ApplicationIdSchema()
        try:

            validated = schema.load({'application_id': application_id})
            if not isinstance(validated, dict):
                return {'errors': f'error with {application_id}'}, 400

            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                Logger.warn(
                    f'Error {token_or_error} getting token from header')
                return token_or_error

            token = token_or_error

            result = ApplicationService.get_job_application(
                token, validated['application_id'])
            if not result:
                return {'msg': 'No application found'}, 404
            return result, 200
        except GenericDatabaseError as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}
        except Exception as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}, 400


class ApplicationUpdateController(Resource):
    @swag_from('../docs/update_application.yml')
    def put(self, application_id):
        id_schema = ApplicationIdSchema()
        schema = JobUpdateSchema()
        try:

            validated = id_schema.load({'application_id': application_id})
            if not isinstance(validated, dict):
                return {'errors': f'error with {application_id}'}, 400

            payload = schema.load(request.get_json())
            if not isinstance(payload, dict):
                return {'errors': f'error validating payload {payload}'}, 400

            token_or_error = get_auth_token()
            if isinstance(token_or_error, tuple):
                Logger.warn(
                    f'Error {token_or_error} getting token from header')
                return token_or_error
            token = token_or_error

            result = ApplicationService.update_an_application(
                token, validated['application_id'], payload['status'])
            if not result:
                return {'msg': f'Application {application_id} was not updated'}, 404
            return {'msg': 'Application update success'}, 200
        except GenericDatabaseError as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}
        except Exception as e:
            Logger.warn(f'{str(e)}')
            return {'error': str(e)}, 400
