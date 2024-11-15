import logging

from src.config import models
from src.config.logger import logger
from src.modules import requests, db, db_methods, parsers




async def update_auth_tokens(domain):
    record = await db_methods.get_record(
        table=db.AuthData,
        condition=db.AuthData.domain == domain
    )

    response = await requests.update_tokens_response(
        refresh_token=record.get('refresh_token'),
        domain=domain
    )

    access_token = response.get('response').get('access_token')
    refresh_token = response.get('response').get('refresh_token')

    if access_token and refresh_token:
        await db_methods.update_record(
            table=db.AuthData,
            condition=db.AuthData.domain == domain,
            **{
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )

        return access_token


async def handle_client_authorization(data):
    code = data.get('code')
    domain = data.get('referer')

    response = await requests.get_tokens_response(
        code=code,
        domain=domain
    )

    access_token = response.get('response').get('access_token')
    refresh_token = response.get('response').get('refresh_token')

    if access_token and refresh_token:
        record = await db_methods.get_record(
            table=db.AuthData,
            condition=db.AuthData.domain == domain
        )

        if record:
            await db_methods.update_record(
                table=db.AuthData,
                condition=db.AuthData.domain == domain,
                **{
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'status': 'Active'
                }
            )

            logger.info(f'Authorization success to new domain: {domain}')

        else:
            response = await requests.get_account_id_response(
                domain=domain,
                access_token=access_token
            )

            account_id = response.get('response').get('id')

            if account_id:
                await db_methods.insert_record(
                    table=db.AuthData,
                    **{
                        'domain': domain,
                        'account_id': account_id,
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'status': 'Active'
                    }
                )

                logger.info(f'Authorization success to domain: {domain}')

            else:
                logger.error(f'Authorization failure to domain: {domain}\nError while getting account_id')

        event_response = await requests.create_event_webhook_response(
            access_token=access_token,
            domain=domain
        )

        if event_response.get('status') == 201 and event_response.get('response').get('created_at'):
            logger.info(f'Event webhook installed to domain: {domain}')

            return 'OK'

        else:
            logger.error(f'Event webhook installation failure\n{event_response}')

    else:
        logger.error(f'Authorization failure to domain: {domain}\n{response}')


async def handle_client_deletion(data):
    account_id = data.get('account_id')

    await db_methods.update_record(
        table=db.AuthData,
        condition=db.AuthData.account_id == account_id,
        **{
            'status': 'Disabled'
        }
    )

    logger.info(f'The client with ID: {account_id} has deleted the application')


async def handle_sending_client_registration_settings(account_id):
    data = await db_methods.get_records(
        table=db.ClientRegister,
        condition=db.ClientRegister.account_id == account_id
    )

    if not data:
        return []

    data_items = [
        models.DataItemModel(
            hash_id=row['hash_id'],
            user_ids=row['user_ids'],
            activity_statuses=row['activity_statuses'],
            custom_questions=row.get('custom_questions', []),
            criterion_questions=row.get('criterion_questions', []),
            destination_user_id=row['destination_user_id'],
            recipient_user_ids=row.get('recipient_user_ids', [])
        )
        for row in data
    ]

    result = models.ClientRegisterModel(
        account_id=data[0]['account_id'],
        data=data_items,
        current_user_id=data[0]['current_user_id']
    )

    return result


async def handle_client_registration_settings(data):
    account_id = data.account_id
    current_user_id = data.current_user_id

    current_settings = await db_methods.get_records(
        table=db.ClientRegister,
        condition=db.ClientRegister.account_id == account_id
    )

    if current_settings:
        await db_methods.delete_records(
            table=db.ClientRegister,
            condition=(db.ClientRegister.account_id == account_id)
        )

    for item in data.data:
        data_dict = {
            'account_id': account_id,
            'hash_id': item.hash_id,
            'user_ids': item.user_ids,
            'activity_statuses': item.activity_statuses,
            'custom_questions': item.custom_questions,
            'criterion_questions': item.criterion_questions,
            'destination_user_id': item.destination_user_id,
            'recipient_user_ids': item.recipient_user_ids,
            'current_user_id': current_user_id
        }

        await db_methods.insert_record(db.ClientRegister, **data_dict)


async def handle_event_notification(form_data):
    data_dict = dict(form_data)

    parsed_data = await parsers.parse_event_data(data_dict=data_dict)

    if parsed_data:
        await db_methods.insert_record(
            table=db.CallData,
            **{
                **parsed_data,
                'status': 'New'
            }
        )

        return 'OK'


async def handle_group_record_data():
    pass


async def handle_record_data():
    pass


async def send_call_data():
    pass


async def send_group_calls_data():
    pass


async def send_results():
    pass
