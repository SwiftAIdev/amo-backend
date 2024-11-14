import logging

from datetime import datetime
from typing import List

import uvicorn

from fastapi import FastAPI, Header, Depends, Request, HTTPException, Response
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

    scheduler.start()

    try:
        db.Base.metadata.create_all(bind=db.engine)

        task_id = 'send_call_data'
        if not scheduler.get_job(job_id=task_id):
            scheduler.add_job(application.send_call_data, id=task_id, next_run_time=datetime.now())

        task_id = 'send_group_calls_data'
        if not scheduler.get_job(job_id=task_id):
            scheduler.add_job(application.send_group_calls_data, CronTrigger(hour=0, minute=0), id=task_id)

        task_id = 'send_results'
        if not scheduler.get_job(job_id=task_id):
            scheduler.add_job(application.send_results, CronTrigger(hour=6, minute=0), id=task_id)

        yield

    finally:
        await db.database.disconnect()

        scheduler.shutdown()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
scheduler = AsyncIOScheduler()


async def verify_token(authorization: str = Header(...)):
    if authorization != cfg.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail='Authentication Error')

    return authorization


@app.get('/service/install')
async def handle_client_authorization_request(
    request: Request
):
    query_params = request.query_params

    status = await application.handle_client_authorization(data=query_params)

    if status == 'OK':
        return {'status': 'OK'}


@app.get('/service/delete')
async def handle_client_deletion_request(
    request: Request
):
    query_params = request.query_params

    status = await application.handle_client_deletion(data=query_params)

    if status == 'OK':
        return {'status': 'OK'}


@app.post('/service/event')
async def handle_event_notification_request(
    request: Request
):
    form_data = await request.form()

    status = await application.handle_event_notification(form_data=form_data)

    if status == 'OK':
        return {'status': 'OK'}


@app.options("/service/client_register")
async def preflight_handler(request: Request):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.get('/service/client_register', response_model=models.ClientRegisterModel)
async def handle_sending_client_registration_settings_request(
    account_id: int,
    token: str = Depends(verify_token)
):
    data = await application.handle_sending_client_registration_settings(account_id=account_id)

    if not data:
        raise HTTPException(status_code=404, detail='Client registration settings not found')

    return data


@app.post('/service/client_register', response_model=models.ClientRegisterModel)
async def handle_client_registration_settings_request(
    data: models.ClientRegisterModel,
    token: str = Depends(verify_token)
):
    try:
        await application.handle_client_registration_settings(data)

        return data

    except Exception as exception:
        logger.error(f'Error while processing client registration settings:\n{exception}', exc_info=True)

        raise HTTPException(status_code=500, detail='Error while processing client registration settings')


# @app.post('/amocrm')  # ПРИЁМ ОДИНОЧНЫХ ЗВОНКОВ ОТ ТРАНСКРИБАТОРА
# async def handle_record_request(
#     data: models.ProcessedCallDataModel,
#     token: str = Depends(verify_token)
# ):
#     try:
#         await application.handle_record_data(data)
#
#         return data
#
#     except Exception as exception:
#         logger.error(f'Error while processing record data:\n{exception}', exc_info=True)
#
#         raise HTTPException(status_code=500, detail='Error, while processing record data')
#
#
# @app.post('/group/amocrm')  # ПРИЁМ ГРУППОВЫХ ЗВОНКОВ ОТ ТРАНСКРИБАТОРА
# async def handle_group_record_request(
#     data: models.ProcessedGroupCallDataModel,
#     token: str = Depends(verify_token)
# ):
#     try:
#         await application.handle_group_record_data(data)
#
#         return data
#
#     except Exception as exception:
#         logger.error(f'Error while processing group record data:\n{exception}', exc_info=True)
#
#         raise HTTPException(status_code=500, detail='Error, while processing group record data')


if __name__ == '__main__':
    logger.info('Starting server...')

    uvicorn.run(app, host=cfg.FASTAPI_HOST, port=cfg.FASTAPI_PORT)
