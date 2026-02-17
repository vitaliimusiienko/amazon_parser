import asyncio
import random
import logging
from functools import wraps
from fake_useragent import UserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_ua: UserAgent | None = None

FALLBACK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def get_random_user_agent() -> str:
    global _ua
    try:
        if _ua is None:
            _ua = UserAgent(os=['windows', 'macos'])
        return _ua.random
    except Exception as e:
        logger.warning(f"UserAgent generation failed: {e}. Using fallback.")
        return random.choice(FALLBACK_USER_AGENTS)

async def random_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> None:
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"Sleeping for {delay:.2f} seconds to mimic human behavior.")
    await asyncio.sleep(delay)

def retry_on_exception(retries: int = 3, base_delay: float = 2.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt} failed with error: {e}")
                    if attempt == retries:
                        logger.error("Max retries reached. Raising exception.")
                        raise

                    jitter = random.uniform(-0.5, 0.5)
                    sleep_time = max(0.0, base_delay * attempt + jitter)
                    await asyncio.sleep(sleep_time)
        return wrapper
    return decorator