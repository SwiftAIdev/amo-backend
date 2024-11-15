from pathlib import Path

from decouple import AutoConfig, config, RepositoryEnv, Choices


def cast_str_to_list(val: str):
    if not val:
        return []

    return val.replace(" ", " ").split(',')

DIR = Path(__file__).absolute().parent.parent.parent

DEPLOYMENT_STAGE = config("DEPLOYMENT_STAGE", cast=Choices(['local', 'dev', 'prod']))

NAME_SERVICE = config("NAME_SERVICE", default="unknown_service")
FASTAPI_PORT = config("FASTAPI_PORT", default=8000, cast=int)

config_env = AutoConfig(f"{DIR}")

file_name_env = f".env.{DEPLOYMENT_STAGE.lower()}"

config_env.SUPPORTED[file_name_env] = RepositoryEnv
config_env.SUPPORTED.move_to_end(file_name_env, last=False)

#  URLS
APPLICATION_URL = config_env("APPLICATION_URL")

#  ENDPOINTS
AUTHENTICATION_ENDPOINT = "/oauth2/access_token"
WEBHOOK_ENDPOINT = "/api/v4/webhooks"
CALLS_ENDPOINT = "/api/v4/calls"
ACCOUNT_ENDPOINT = "/api/v4/account"
CONTACTS_ENDPOINT = "/api/v4/contacts"
LEADS_ENDPOINT = "/api/v4/leads"

#  TOKENS
AUTH_TOKEN = config_env("AUTH_TOKEN")

#  AUTH
CLIENT_ID = config_env("CLIENT_ID")
CLIENT_SECRET = config_env("CLIENT_SECRET")
YC_TOKEN = config_env("YC_TOKEN")
YC_GROUP_ID = config_env("YC_GROUP_ID")


#  SERVICE
FASTAPI_HOST = config_env("FASTAPI_HOST")
FASTAPI_ORIGINS = config_env("FASTAPI_ORIGINS", cast=cast_str_to_list)

DATABASE_NAME = config_env("DATABASE_NAME")
DATABASE_USER_NAME = config_env("DATABASE_USER_NAME")
DATABASE_USER_PASSWORD = config_env("DATABASE_USER_PASSWORD")
DATABASE_HOST = config_env("DATABASE_HOST")
DATABASE_PORT = config_env("DATABASE_PORT", cast=int)

DATABASE_USER_DATA = f"{DATABASE_USER_NAME}:{DATABASE_USER_PASSWORD}" if len(DATABASE_USER_PASSWORD) > 0 else DATABASE_USER_NAME
DATABASE_PORT_AND_HOST = f"{DATABASE_HOST}:{DATABASE_PORT}" if DATABASE_PORT > 0 else DATABASE_HOST
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER_DATA}@{DATABASE_PORT_AND_HOST}/{DATABASE_NAME}"
