import os


#  URLS
APPLICATION_URL = os.getenv('APPLICATION_URL')

# ENDPOINTS
AUTHENTICATION_ENDPOINT = '/oauth2/access_token'
WEBHOOK_ENDPOINT = '/api/v4/webhooks'
CALLS_ENDPOINT = '/api/v4/calls'
ACCOUNT_ENDPOINT = '/api/v4/account'
CONTACTS_ENDPOINT = '/api/v4/contacts'
LEADS_ENDPOINT = '/api/v4/leads'

#  TOKENS
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

#  AUTH
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

#  SERVICE
FASTAPI_HOST = os.getenv('FASTAPI_HOST')
FASTAPI_PORT = int(os.getenv('FASTAPI_PORT'))

#  DATABASE
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST')
}
