import logging

from src.config import cfg
from src.modules import routes, db, db_methods

logger = logging.getLogger(__name__)


async def get_account_id(access_token, domain):
    response = await routes.send_request(
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

    return str(response.get('id'))


async def get_tokens(code, domain):
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


async def update_tokens(refresh_token, domain):
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


async def create_event_webhook(access_token, domain):
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


async def remove_event_webhook(access_token, domain):
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

    response = await update_tokens(
        refresh_token=record.get('refresh_token'),
        domain=domain
    )

    if response.get('access_token') and response.get('refresh_token'):
        await db_methods.update_record(
            table=db.AuthData,
            domain=domain,
            **{
                'access_token': response.get('access_token'),
                'refresh_token': response.get('refresh_token')
            }
        )

        return 'OK'
