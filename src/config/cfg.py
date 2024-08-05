from decouple import config

#  URLS
APPLICATION_URL = 'https://d3c7-95-26-151-140.ngrok-free.app'

# ENDPOINTS
AUTHENTICATION_ENDPOINT = '/oauth2/access_token'
WEBHOOK_ENDPOINT = '/api/v4/webhooks'
CALLS_ENDPOINT = '/api/v4/calls'
ACCOUNT_ENDPOINT = '/api/v4/account'

#  TOKENS
AUTH_TOKEN = config('AUTH_TOKEN', default='pvzFZgtYsUyB5X9tS52Ducm9Cz5VCRr4jsImRIrovKM80Wc86WA7LSHoAERf1wVKMKuWxWug2DKI6ZtMuCc4UDeKUkHM9Ve8vQEYMRzo1MRDkCJY24TMQTiBv2DyYKiJ')

#  AUTH
CLIENT_ID = '93fab18a-7a7c-4edf-861d-e5435e8c3695'
CLIENT_SECRET = '1TQBRbBYxRmZajtEIpxtSY8pIuVKnFbuxLakgjkQHIBEOlGPjAo9n43dKT0XZgJL'

#  SERVICE
FASTAPI_HOST = config('FASTAPI_HOST', default='localhost')
FASTAPI_PORT = config('FASTAPI_PORT', default='8000', cast=int)

#  DATABASE
DB_CONFIG = {
    'user': config('DATABASE_USER_NAME', default='postgres'),
    'password': config('DATABASE_USER_PASSWORD', default='1tc3gpoM'),
    'database': config('DATABASE_NAME', default='amo'),
    'host': config('DATABASE_HOST', default='localhost')
}
