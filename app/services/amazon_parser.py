import re
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


async def safe_extract_text(page: Page, selector: str) -> str | None:
    try:
        element = await page.query_selector(selector)
        if element:
            text = await element.inner_text()
            return text.strip()
    except Exception as e:
        logger.debug(f"Error extracting text with selector '{selector}': {e}")
    return None

async def parse_product_page(page: Page, url: str, rank: int) -> dict:
    logger.info(f"Parsing product page: {url} (Rank #{rank})")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await random_delay(1.5, 3)
    except Exception as e:
        logger.error(f"Error loading page {url}: {e}")
        raise

    asin = None
    if "/dp/" in url:
        asin = url.split("/dp/")[1].split("/")[0].split("?")[0]

    title = await safe_extract_text(page, "#productTitle")
    if not title:
        logger.warning(f"Title not found for ASIN {asin} at URL {url}")
        return None

    def parse_price(price_str: str) -> float | None:
        if not price_str:
            return None
        clean = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(clean) if clean else None
        except ValueError:
            logger.warning(f"Could not parse price: '{price_str}'")
            return None

    price_str = (
        await safe_extract_text(page, "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen")
        or await safe_extract_text(page, "#priceblock_ourprice")
    )
    price = parse_price(price_str)

    list_price_str = await safe_extract_text(page, ".a-text-price .a-offscreen")
    list_price = parse_price(list_price_str)

    discount_percent = None
    if price and list_price and list_price > price:
        discount_percent = int(((list_price - price) / list_price) * 100)

    rating = None
    rating_str = await safe_extract_text(page, "#acrPopover")
    if rating_str:
        match = re.search(r'([\d.]+)', rating_str)
        if match:
            rating = float(match.group(1))

    reviews_count = None
    reviews_str = await safe_extract_text(page, "#acrCustomerReviewText")
    if reviews_str:
        clean_reviews = re.sub(r'[^\d]', '', reviews_str)
        if clean_reviews:
            reviews_count = int(clean_reviews)

    is_prime = await page.query_selector("i.a-icon-prime") is not None

    best_sellers_rank = await safe_extract_text(page, "#SalesRank")
    if best_sellers_rank:
        best_sellers_rank = " ".join(best_sellers_rank.split())

    bullet_points = []
    bullet_elements = await page.query_selector_all("#feature-bullets ul li span.a-list-item")
    for elem in bullet_elements:
        text = (await elem.inner_text()).strip()
        if text and len(bullet_points) < 5:
            bullet_points.append(text)

    main_image_url = None
    img_element = await page.query_selector("#landingImage")
    if img_element:
        main_image_url = await img_element.get_attribute("src")

    return {
        "asin": asin,
        "title": title,
        "rank": rank,
        "price": price,
        "list_price": list_price,
        "discount_percent": discount_percent,
        "rating": rating,
        "reviews_count": reviews_count,
        "is_prime": is_prime,
        "best_sellers_rank": best_sellers_rank,
        "bullet_points": bullet_points,
        "main_image_url": main_image_url,
    }