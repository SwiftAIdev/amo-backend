import logging

import aiohttp


logger = logging.getLogger(__name__)


async def send_request(method, url, endpoint, headers, params):
    try:
        async with aiohttp.ClientSession() as session:
            request_methods = {
                'get': session.get,
                'post': session.post,
                'put': session.put,
                'delete': session.delete
            }

            if method in request_methods:
                async with request_methods[method](url=f'{url}{endpoint}', headers=headers, json=params) as response:
                    try:
                        response.raise_for_status()

                        return await response.json()

                    except aiohttp.ContentTypeError:
                        logger.info('Answer in not in JSON format, returning "OK"')

                        return 'OK'

                    except aiohttp.ClientResponseError as exception:
                        if exception.status == 401:
                            logger.info('Access token is expired', exc_info=True)

                            return 'Token'

                        else:
                            logger.error(f'HTTP error:\n{exception.status} - {exception.message}', exc_info=True)

            else:
                logger.error(f'Invalid method "{method}"', exc_info=True)

    except Exception as exception:
        logger.error(f'Error while sending request:\n{exception}', exc_info=True)
