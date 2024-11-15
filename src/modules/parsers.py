import json

from src.config.logger import logger
from src.modules import requests, db, db_methods


async def parse_event_data(data_dict):
    activity_type = next((value for key, value in data_dict.items() if key.endswith('[type]')), None)

    if activity_type == 'contact':
        parsers_list = [parse_sipuni_telephony_data, parse_other_telephony_data]

        for parser in parsers_list:
            result = await parser(data_dict=data_dict)

            if result is not None:
                return result


async def extract_invariable_contact_data(data_dict):
    try:
        account_id = int(data_dict.get('account[id]'))

    except ValueError:
        logger.error(f'Inconsistent event data, error while fetching account_id', exc_info=True)

        return None

    record = await db_methods.get_record(
        table=db.AuthData,
        condition=db.AuthData.account_id == account_id
    )

    if not record:
        logger.error(f'No client with this account_id', exc_info=True)

        return None

    response = await requests.get_contact_data_response(
        access_token=record.get('access_token'),
        domain=record.get('domain'),
        contact_id=data_dict.get('contacts[note][0][note][element_id]')
    )

    links = response.get('response', {}).get('_embedded', {}).get('links', [])
    deal_id = next((link.get('to_entity_id') for link in links if link.get('to_entity_type') == 'leads'), None)

    if not deal_id:
        logger.info(f'No deals associated with this contact_id')

        return None

    response = await requests.get_deal_data_response(
        access_token=record.get('access_token'),
        domain=record.get('domain'),
        deal_id=deal_id
    )

    try:
        activity_id = int(data_dict.get('contacts[note][0][note][element_id]'))
        note_id = int(data_dict.get('contacts[note][0][note][id]'))
        user_id = int(data_dict.get('contacts[note][0][note][created_by]'))

    except ValueError:
        logger.error(f'Inconsistent event data, error while fetching invariable contact data rows', exc_info=True)

        return None

    return {
        'account_id': account_id,
        'client_endpoint': data_dict.get('account[_links][self]'),
        'activity_type': 'contact',
        'activity_id': activity_id,
        'note_id': note_id,
        'user_id': user_id,
        'pipeline_id': response.get('response', {}).get('pipeline_id', None),
        'status_id': response.get('response', {}).get('status_id', None)
    }


async def parse_sipuni_telephony_data(data_dict):
    invariable_data = await extract_invariable_contact_data(data_dict=data_dict)

    try:
        telephony_data = json.loads(data_dict.get('contacts[note][0][note][text]'))

        return {
            **invariable_data,
            'call_id': telephony_data.get('UNIQ'),
            'call_url': telephony_data.get('LINK'),
            'call_duration': telephony_data.get('DURATION')
        }

    except json.JSONDecodeError as exception:
        logger.error(f'Error while JSON decoding:\n{exception}', exc_info=True)


async def parse_other_telephony_data(data_dict):
    try:
        return None

    except (json.JSONDecodeError, KeyError, TypeError):
        return None
