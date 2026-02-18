import asyncio
import random
import logging
from functools import wraps
from playwright.async_api import Page

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)


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


async def set_us_location(page: Page):
    try:
        logger.info("Change location to US...")
        loc_btn = await page.wait_for_selector(
            "#nav-global-location-popover-link", timeout=10000
        )
        await page.wait_for_timeout(2000)
        if loc_btn:
            await loc_btn.click()
        await page.wait_for_selector("#GLUXZipUpdateInput", timeout=10000)
        await page.fill("#GLUXZipUpdateInput", "10001")
        await page.wait_for_timeout(500)

        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)

        done_btn = await page.query_selector(".a-popover-footer #GLUXConfirmClose")
        if done_btn:
            await done_btn.click()
            await page.wait_for_timeout(1000)
        await page.reload(wait_until="domcontentloaded")

        logger.info("Location successfully changed and page reloaded!")

    except Exception as e:
        logger.warning(f"Failed change location: {e}")
