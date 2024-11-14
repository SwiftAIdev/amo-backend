import logging

from src.config import cfg
from src.modules import routes, decorators

logger = logging.getLogger(__name__)


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
            'redirect_uri': f'{cfg.APPLICATION_URL}/service/install'
        }
    )


@decorators.retry_on_token_expired
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


@decorators.retry_on_token_expired
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
            'settings': ['note_contact']
        }
    )


@decorators.retry_on_token_expired
async def get_contact_data_response(access_token, domain, contact_id):
    return await routes.send_request(
        method='get',
        url=f'https://{domain}',
        endpoint=f'{cfg.CONTACTS_ENDPOINT}/{contact_id}/links',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        params={}
    )


@decorators.retry_on_token_expired
async def get_deal_data_response(access_token, domain, deal_id):
    return await routes.send_request(
        method='get',
        url=f'https://{domain}',
        endpoint=f'{cfg.LEADS_ENDPOINT}/{deal_id}',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        params={}
    )
