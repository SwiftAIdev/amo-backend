import functools

from src.config.logger import logger
from src.modules import application


def retry_on_token_expired(func):
    @functools.wraps(func)
    async def wrapper(**kwargs):
        result = await func(**kwargs)

        status = result.get('status')

        if status == 401 and result.get('response').get('detail') == 'Неверный логин или пароль':
            kwargs['access_token'] = await application.update_auth_tokens(kwargs.get('domain'))

            result = await func(**kwargs)

            status = result.get('status')
            response = result.get('response')
            detail = response.get('detail')

            if status == 401 and detail == 'Неверный логин или пароль':
                logger.error(f'Retry after token update also failed with error: {detail}', exc_info=True)

                return {'status': status, 'response': response}

            else:
                logger.error(f'Retry after token update failed with another error: {detail}', exc_info=True)

                return {'status': status, 'response': response}

        return result

    return wrapper
