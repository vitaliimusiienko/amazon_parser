import logging
from playwright.async_api import async_playwright, Page
from app.utils.anti_block import get_random_user_agent, random_delay, retry_on_exception

logger = logging.getLogger(__name__)

async def inject_stealth(page: Page):
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
                })
    """)

@retry_on_exception(retries=3)
async def get_top_5_product_url(category_url: str) -> list[str]:
    urls = []

    logger.info(f"Launching Playwright to scrape Amazon category: {category_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        try:
            context = await browser.new_context(user_agent=get_random_user_agent(),
                                            viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            await inject_stealth(page)
            
            await page.goto(category_url, wait_until='domcontentloaded', timeout=60000)
            await random_delay(2, 4)

            link_elements = await page.query_selector_all("a[href*='/dp/']")

            for elem in link_elements:
                href = await elem.get_attribute('href')
                if href and '/dp/' in href:
                    full_url = f"https://www.amazon.com{href}" if href.startswith('/') else href
                    clean_url = full_url.split("?")[0].split("ref=")[0]
                    if clean_url not in urls:
                        urls.append(clean_url)

                if len(urls) >= 5:
                    break
        finally:
            await browser.close()

    logger.info(f"Extracted {len(urls)} product URLs from category.")
    return urls