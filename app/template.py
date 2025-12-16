import os
from dotenv import load_dotenv

load_dotenv()


def get_swagger_host_and_schemes():
    env = os.getenv('ENV')
    host = '127.0.0.1:5005'
    render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if env == 'dev':
        schemes = ['http']
        host = host
    else:
        schemes = ['https']
        host = render_host

    return host, schemes


SWAGGER_HOST, SWAGGER_SCHEMES = get_swagger_host_and_schemes()


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
    'host': SWAGGER_HOST,
    'schemes': SWAGGER_SCHEMES,
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization using the Bearer scheme. Example: `Bearer {token}`'
        }
    }

}
