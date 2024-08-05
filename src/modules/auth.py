import logging
import functools


from src.config import cfg
from src.modules import routes, db, db_methods

logger = logging.getLogger(__name__)


def retry_on_token_expired(func):
    @functools.wraps(func)
    async def wrapper(**kwargs):
        result = await func(**kwargs)

        if result == 'Token':
            logger.info('Token updating...')

            domain = kwargs.get('domain')

            kwargs['access_token'] = await update_auth_tokens(domain)

            result = await func(**kwargs)

        return result

    return wrapper


async def get_tokens_response(code, domain):
    return await routes.send_request(
        method='post',
        url=f'https://{domain}',
        endpoint=cfg.AUTHENTICATION_ENDPOINT,
        headers={
            'Content-Type': 'application/json'
        },
        params={
            'client_id': cfg.CLIENT_ID,
            'client_secret': cfg.CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f'{cfg.APPLICATION_URL}/service/install'
        }
    )


@retry_on_token_expired
async def update_tokens_response(refresh_token, domain):
    return await routes.send_request(
        method='post',
        url=f'https://{domain}',
        endpoint=cfg.AUTHENTICATION_ENDPOINT,
        headers={
            'Content-Type': 'application/json'
        },
        params={
            'client_id': cfg.CLIENT_ID,
            'client_secret': cfg.CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'redirect_uri': cfg.APPLICATION_URL
        }
    )


@retry_on_token_expired
async def get_account_id_response(access_token, domain):
    return await routes.send_request(
        method='get',
        url=f'https://{domain}',
        endpoint=cfg.ACCOUNT_ENDPOINT,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        params={
            'with': 'id'
        }
    )


@retry_on_token_expired
async def create_event_webhook_response(access_token, domain):
    return await routes.send_request(
        method='post',
        url=f'https://{domain}',
        endpoint=cfg.WEBHOOK_ENDPOINT,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        params={
            'destination': f'{cfg.APPLICATION_URL}/service/event',
            'settings': [
                'note_lead',
                'note_contact',
                'note_company'
            ]
        }
    )


@retry_on_token_expired
async def remove_event_webhook_response(access_token, domain):
    return await routes.send_request(
        method='delete',
        url=f'https://{domain}',
        endpoint=cfg.WEBHOOK_ENDPOINT,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        params={
            'destination': f'{cfg.APPLICATION_URL}/service/event'
        }
    )


async def update_auth_tokens(domain):
    record = await db_methods.get_record(
        table=db.AuthData,
        condition=db.AuthData.domain == domain
    )

    response = await update_tokens_response(
        refresh_token=record.get('refresh_token'),
        domain=domain
    )

    access_token = response.get('access_token')
    refresh_token = response.get('refresh_token')

    if access_token and refresh_token:
        await db_methods.update_record(
            table=db.AuthData,
            domain=domain,
            **{
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )

        return access_token
