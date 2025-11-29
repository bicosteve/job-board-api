from typing import cast

from flask import make_response, jsonify
from flask_restful import Resource, request
from marshmallow import ValidationError
from flasgger import swag_from

from ..schemas.job import JobSchema
from ..services.job_service import JobService
from ..utils.logger import Logger


class PostJobController(Resource):

    @swag_from('../docs/create_job.yml')
    def post(self):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                Logger.warn("No authorization token in the header")
                return {'validation_err': 'Unauthorized'}, 401

            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            else:
                return {'error': 'Invalid auth header format'}, 401

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
