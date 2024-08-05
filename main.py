import logging

from datetime import datetime

import uvicorn

from fastapi import FastAPI, Header, Depends, Request, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager

from src.config import cfg
from src.config import models
from src.modules import application, db
from src.config.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.database.connect()

    # scheduler.start()

    try:
        db.Base.metadata.create_all(bind=db.engine)

        # task_id = 'send_call_data'
        # if not scheduler.get_job(job_id=task_id):
        #     scheduler.add_job(application.send_call_data, id=task_id, next_run_time=datetime.now())
        #
        # task_id = 'send_group_calls_data'
        # if not scheduler.get_job(job_id=task_id):
        #     scheduler.add_job(application.send_group_calls_data, CronTrigger(hour=0, minute=0), id=task_id)
        #
        # task_id = 'send_results'
        # if not scheduler.get_job(job_id=task_id):
        #     scheduler.add_job(application.send_results, CronTrigger(hour=6, minute=0), id=task_id)

        yield

    finally:
        await db.database.disconnect()

        # scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
# scheduler = AsyncIOScheduler()


async def verify_token(authorization: str = Header(...)):
    if authorization != cfg.AUTH_TOKEN:
        raise HTTPException(status_code=400, detail='Authentication Error')

    return authorization


@app.get('/service/install')
async def handle_client_authorization_data(
    request: Request
):
    query_params = request.query_params

    status = await application.handle_client_authorization(data=query_params)

    if status == 'OK':
        return {'status': 'OK'}


@app.get('/service/delete')
async def handle_client_deletion_data(
    request: Request
):
    query_params = request.query_params

    status = await application.handle_client_deletion(data=query_params)

    if status == 'OK':
        return {'status': 'OK'}


@app.post('/service/call_data', response_model=models.CallDataModel)
async def handle_call_data(
    data: models.CallDataModel,
    token: str = Depends(verify_token)
):
    try:
        await application.handle_call_data(data)

        return data

    except Exception as exception:
        logger.error(f'Error while receiving call data:\n{exception}', exc_info=True)

        raise HTTPException(status_code=500, detail='Error, while receiving call data')


@app.post('/service/client_register', response_model=models.ClientRegisterModel)
async def handle_client_registration_data(
    data: models.ClientRegisterModel,
    token: str = Depends(verify_token)
):
    try:
        await application.handle_client_registration(data)

        return data

    except Exception as exception:
        logger.error(f'Error while client registration:\n{exception}', exc_info=True)

        raise HTTPException(status_code=500, detail='Error, while client registration')


@app.post('/amocrm')
async def handle_record_request(
    data: models.ProcessedCallDataModel,
    token: str = Depends(verify_token)
):
    try:
        await application.handle_record_data(data)

        return data

    except Exception as exception:
        logger.error(f'Error while processing record data:\n{exception}', exc_info=True)

        raise HTTPException(status_code=500, detail='Error, while processing record data')


@app.post('/group/amocrm')
async def handle_group_record_request(
    data: models.ProcessedGroupCallDataModel,
    token: str = Depends(verify_token)
):
    try:
        await application.handle_group_record_data(data)

        return data

    except Exception as exception:
        logger.error(f'Error while processing group record data:\n{exception}', exc_info=True)

        raise HTTPException(status_code=500, detail='Error, while processing group record data')


###############
@app.post('/service/event')
async def handle_record_request_test(
    request: Request
):
    form_data = await request.form()

    print(form_data)
##############


if __name__ == '__main__':
    logger.info('Starting server...')
    uvicorn.run(app, host=cfg.FASTAPI_HOST, port=cfg.FASTAPI_PORT)
