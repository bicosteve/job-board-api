import os
from dotenv import load_dotenv

load_dotenv()

swagger_template = {
    'info': {
        'title' : 'Job Board API',
        'description': 'API Documentation for the Job Board System',
        'version': os.getenv('API_VERSION', '1.0.0'),
        'contact': {
            'name': os.getenv('CONTACT_NAME', 'bix'),
            'email': os.getenv('CONTACT_EMAIL', 'test@example.com')
        }
    },
    'basePath': '/',
    'schemes': ['http', 'https'],
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization using the Bearer scheme. Example: `Bearer {token}`'
        }
    }

}
