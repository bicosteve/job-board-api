from flask import current_app, request
from flask_restful import Resource

from ..services.file_service import FileService
from ..utils.security import Security
from ..utils.logger import Logger
from ..utils.exceptions import InvalidCredentialsError


# Helpers
def get_auth_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        Logger.warn('No authorization token in the header')
        return {'validation_err': 'Unauthorized'}, 401

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    return {'error': 'Invalid auth header format'}, 401


class FileUploadController(Resource):
    def post(self):
        token_or_error = get_auth_token()
        if isinstance(token_or_error, tuple):
            return token_or_error

        token = token_or_error
        decoded = Security.decode_jwt_token(token)
        if not decoded or not decoded.get('profile_id'):
            raise InvalidCredentialsError('Invalid upload credentials')

        if 'file' not in request.files:
            return {'error': 'Missing file upload'}, 400

        upload_file = request.files['file']
        if upload_file.filename == '':
            return {'error': 'No file selected'}, 400

        if not FileService.is_allowed_file(upload_file.filename):
            return {'error': 'Unsupported file type. Allowed: pdf, doc, docx, txt'}, 400

        try:
            filename = FileService.save_uploaded_file(upload_file, current_app.config['UPLOAD_FOLDER'])
            host_url = request.host_url.rstrip('/')
            file_url = f"{host_url}/uploads/{filename}"
            return {'file_url': file_url}, 201
        except Exception as exc:
            Logger.error(f'Failed to save uploaded file: {str(exc)}')
            return {'error': str(exc)}, 500
