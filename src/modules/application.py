import logging

from sqlalchemy import update
from src.modules import auth, db, db_methods
from src.config import models

logger = logging.getLogger(__name__)


async def handle_client_authorization(data):
    code = data.get('code')
    domain = data.get('referer')

    auth_response = await auth.get_tokens_response(
        code=code,
        domain=domain
    )

    access_token = auth_response.get('access_token')
    refresh_token = auth_response.get('refresh_token')

    if access_token and refresh_token:
        record = await db_methods.get_record(
            table=db.AuthData,
            condition=db.AuthData.domain == domain
        )

        if record:
            await db_methods.update_record(
                table=db.AuthData,
                domain=domain,
                **{
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            )

            logger.info(f'Authorization success to new domain: {domain}')

        else:
            response = await auth.get_account_id_response(
                domain=domain,
                access_token=access_token
            )

            account_id = str(response.get('id'))

            if account_id:
                await db_methods.insert_record(
                    table=db.AuthData,
                    domain=domain,
                    **{
                        'account_id': account_id,
                        'access_token': access_token,
                        'refresh_token': refresh_token
                    }
                )

                logger.info(f'Authorization success to domain: {domain}')

            else:
                logger.error(f'Authorization failure to domain: {domain}\nError while getting account_id')

        event_response = await auth.create_event_webhook_response(
            access_token=access_token,
            domain=domain
        )

        if event_response.get('created_at'):
            logger.info(f'Event webhook installed to domain: {domain}')

            return 'OK'

        else:
            logger.error(f'Event webhook installation failure\n{event_response}')

    else:
        logger.error(f'Authorization failure to domain: {domain}\n{auth_response}')


async def handle_client_deletion(data):
    record = await db_methods.get_record(
        table=db.AuthData,
        condition=db.AuthData.account_id == data.get('account_id')
    )

    if record:
        access_token = record.get('access_token')
        domain = record.get('domain')

        event_response = await auth.remove_event_webhook_response(
            access_token=access_token,
            domain=domain
        )

        if event_response == 'OK':
            logger.info(f'Event webhook deletion success to domain: {domain}')

            return 'OK'

        else:
            logger.error(f'Event webhook deletion failure\n{event_response}')

    else:
        logger.error(f'Event webhook deletion failure\nError while getting auth_data from database')


async def handle_client_registration(data):
    serialized_data = data.model_dump()

    serialized_data = {key: value for key, value in serialized_data.items() if value is not None}

    query = db.ClientRegister.__table__.insert().values(
        **serialized_data
    )

    await db.database.execute(query)


async def handle_call_data(data):
    query = db.CallData.__table__.insert().values(
        **data.model_dump(exclude='status'), status='1'
    )

    await db.database.execute(query)


async def handle_group_record_data(data):
    query = db.GroupCallData.__table__.insert().values(
        **data.model_dump(exclude='status'), status='Not sent'
    )

    await db.database.execute(query)


async def handle_record_data(data: models.ProcessedCallDataModel):
    query = (
        update(db.CallData)
        .where(db.CallData.call_id == data.call_id)
        .where(db.CallData.domain == data.domain)
        .values(transcription=data.transcription, summary=data.summary, status='3')
    )

    await db.database.execute(query)


async def send_call_data():
    pass


async def send_group_calls_data():
    pass


async def send_results():
    pass
