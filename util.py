import logging
from datetime import datetime
import time
import pytz

logging.basicConfig(filename='output.log', level=logging.INFO)
logger = logging.getLogger()


def wait(timeout=120):
    def decorator(f):
        def wrapper(*args, **kwargs):
            logger.info(f'{timestamp()} - sleeping for {timeout} seconds before calling {f.__name__} ...')
            time.sleep(timeout)
            # value_if_true if condition else value_if_false
            logger.info(
                f'{timestamp()} - running {f.__name__} {"with" if args or kwargs else ""} {args if args else ""} {kwargs if kwargs else ""}')
            return f(*args, **kwargs)

        return wrapper

    return decorator


def timestamp():
    timezone = pytz.timezone('Europe/Berlin')
    now = timezone.localize(datetime.now())
    return now.strftime("%d-%m-%Y %H:%M:%S")


if __name__ == '__main__':
    foo("fed")
