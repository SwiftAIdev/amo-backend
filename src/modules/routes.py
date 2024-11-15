import aiohttp

from src.config.logger import logger


async def send_request(method, url, endpoint, headers, params=None, json_data=None):
    try:
        async with aiohttp.ClientSession() as session:
            if method.lower() in ['get', 'post', 'put', 'delete']:
                request_function = getattr(session, method.lower())

            else:
                logger.error(f'Invalid HTTP method "{method}"', exc_info=True)

                return {
                    'status': 0,
                    'response': 'Error: Invalid HTTP method'
                }

            async with request_function(url=f'{url}{endpoint}', headers=headers, params=params, json=json_data) as response:
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

    except Exception as exception:
        logger.error(f'Error while sending request:\n{exception}', exc_info=True)

        return {
            'status': 0,
            'response': 'Error: Exception occurred'
        }
