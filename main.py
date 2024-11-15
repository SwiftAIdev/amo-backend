import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Header, Depends, Request, HTTPException, Response
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from src.config import cfg
from src.config import models
from src.config.cfg import FASTAPI_HOST, FASTAPI_PORT
from src.config.logger import  logger
from src.modules import application, db
from src.utils.health_check import HealthCheckResponse, check_database
from src.utils.logger import log_context, LoggingMiddleware


async def verify_token(authorization: str = Header(...)):
    if authorization != cfg.AUTH_TOKEN:
        raise HTTPException(status_code=401, detail='Authentication Error')

    return authorization


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


scheduler = AsyncIOScheduler()
start_time = time.time()
app = FastAPI(lifespan=lifespan, title="SwiftAI - Amo Service", root_path="/amo_service/api", docs_url=None, redoc_url=None)

app.logger = logger
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def add_request_id_to_logs(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

    request.state.request_id = request_id

    with log_context({"x_request_id": request_id}):
        response = await call_next(request)

        response.headers['X-Request-ID'] = request_id

        return response

@app.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
async def health_check():

    db_status = await check_database()
    uptime_seconds = int(time.time() - start_time)
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    uptime = f"{uptime_hours}h {uptime_minutes}m"

    service_status = "ok" if db_status == "connected" else "degraded"
    details = {
        "database": db_status,
        "uptime": uptime
    }
    logger.info({
        "message":"health_check",
        "details":details,
    })
    return HealthCheckResponse(
        status=service_status,
        details=details
    )
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

    uvicorn.run(app="main:app", host=FASTAPI_HOST, port=FASTAPI_PORT, workers=1, use_colors=True)
