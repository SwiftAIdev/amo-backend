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

            request_function = request_methods.get(method.lower())

            if request_function:
                async with request_function(url=f'{url}{endpoint}', headers=headers, json=params) as response:
                    status = response.status

                    try:
                        return {
                            'status': status,
                            'response': await response.json()
                        }

                    except aiohttp.ContentTypeError:
                        logger.info('Answer in not in JSON format')

                        return {
                            'status': status,
                            'response': 'No JSON data'
                        }

            else:
                logger.error(f'Invalid method "{method}"', exc_info=True)

                return {
                    'status': 0,
                    'response': 'Error: Invalid HTTP method'
                }

    except Exception as exception:
        logger.error(f'Error while sending request:\n{exception}', exc_info=True)

        return {
            'status': 0,
            'response': 'Error: Exception occurred'
        }
