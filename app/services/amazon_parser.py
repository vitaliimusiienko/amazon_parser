import re
from typing import Any
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from playwright.async_api import async_playwright, BrowserContext

from app.utils.anti_block import (
    get_random_user_agent,
    random_delay,
    retry_on_exception,
    set_us_location,
)
from app.config import settings
from app.utils.logger import setup_logger
from app.utils.selectors import AmazonSelectors

logger = setup_logger(__name__)


# ==================== UTILITY FUNCTIONS ====================
@asynccontextmanager
async def get_browser_context() -> AsyncGenerator[BrowserContext, None]:
    async with async_playwright() as p:
        browser_kwargs: dict[str, Any] = {"headless": settings.BROWSER_HEADLESS}
        proxy_config = get_proxy_config()
        if proxy_config:
            browser_kwargs["proxy"] = proxy_config

        browser = await p.chromium.launch(**browser_kwargs)

        try:
            context = await browser.new_context(
                user_agent=get_random_user_agent(),
                viewport={"width": 1920, "height": 1080},
            )
            yield context
        finally:
            if "context" in locals():
                await context.close()
            await browser.close()


def get_proxy_config() -> dict | None:
    """Parse proxy URL from settings into Playwright-compatible format."""
    if not settings.PROXY_URL:
        return None

    parsed = urlparse(settings.PROXY_URL)
    if parsed.username and parsed.password:
        return {
            "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
            "username": parsed.username,
            "password": parsed.password,
        }
    return {"server": settings.PROXY_URL}


def parse_price(price_str: str | None) -> float | None:
    """
    Extract numeric price from string with currency symbol or code.
    Supports: $123.45, USD123.45, AUD 123.45
    """
    if not price_str:
        return None

    # Remove all whitespace including non-breaking spaces
    clean_str = price_str.replace("\xa0", "").replace(" ", "")

    # Match price after $ or 3-letter currency code
    match = re.search(r"(?:\$|[A-Z]{3})([\d,]+\.?\d*)", clean_str)
    if not match:
        return None

    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:
        logger.warning(f"Could not parse price: '{price_str}'")
        return None


def parse_currency(price_str: str | None) -> str | None:
    if not price_str:
        return None
    clean_str = price_str.replace("\xa0", "").replace(" ", "")
    match = re.search(r"([$€£¥]|(?:[A-Z]{3}))", clean_str)

    if match:
        symbol = match.group(1).upper()
        currency_map = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
        return currency_map.get(symbol, symbol)

    return None


def parse_discount(discount_str: str | None) -> int | None:
    """Extract discount percentage from string like '-20%' or '20% off'."""
    if not discount_str:
        return None

    match = re.search(r"-?\s*(\d+)%", discount_str)
    return int(match.group(1)) if match else None


# ==================== PAGE HELPERS ====================


async def inject_stealth(page: Page) -> None:
    """Inject JavaScript to mask browser automation markers."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    """)


async def bypass_soft_block(page: Page) -> bool:
    """
    Handle Amazon's soft block (location confirmation page).
    Returns True if block was detected and bypassed.
    """
    try:
        continue_btn = await page.query_selector("text='Continue shopping'")

        if continue_btn:
            logger.warning("Detected soft block, bypassing...")
            await continue_btn.click()
            await page.wait_for_load_state("domcontentloaded")
            await random_delay(1.5, 3)
            logger.info("Soft block bypassed successfully")
            return True

        return False
    except Exception as e:
        logger.debug(f"Error checking for soft block: {e}")
        return False


async def safe_extract_text(page: Page, selectors: list[str] | str) -> str | None:
    """
    Try multiple selectors until one returns non-empty text.
    Returns first non-empty match or None.
    """
    if isinstance(selectors, str):
        selectors = [selectors]

    for selector in selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                if text and text.strip():
                    return text.strip()
        except Exception:
            continue

    return None


# ==================== MAIN SCRAPING FUNCTIONS ====================


@retry_on_exception(retries=3)
async def get_top_5_product_url(category_url: str) -> list[str]:
    """
    Extract top 5 product URLs from Amazon category page.
    Returns list of clean product URLs without query parameters.
    """
    urls: list[str] = []
    logger.info(f"Scraping category: {category_url}")

    async with get_browser_context() as context:
        page = await context.new_page()
        await inject_stealth(page)

        await page.goto(category_url, wait_until="domcontentloaded", timeout=60000)
        await random_delay(2, 4)
        await bypass_soft_block(page)

        # Find all product links
        link_elements = await page.query_selector_all("a[href*='/dp/']")

        for elem in link_elements:
            href = await elem.get_attribute("href")
            if href and "/dp/" in href:
                # Normalize URL
                full_url = (
                    f"https://www.amazon.com{href}" if href.startswith("/") else href
                )
                clean_url = full_url.split("?")[0].split("ref=")[0]

                if clean_url not in urls:
                    urls.append(clean_url)

            if len(urls) >= 5:
                break

    logger.info(f"Extracted {len(urls)} product URLs")
    return urls


async def parse_product_page(page: Page, url: str, rank: int) -> dict | None:
    """
    Parse detailed product information from Amazon product page.
    Returns dict with product data or None if parsing fails.
    """
    logger.info(f"Parsing product page: {url} (Rank #{rank})")

    # Extract ASIN from URL
    asin = None
    if "/dp/" in url:
        asin = url.split("/dp/")[1].split("/")[0].split("?")[0]

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await random_delay(1.5, 3)
        await bypass_soft_block(page)
    except Exception as e:
        logger.error(f"Error loading page {url} (ASIN: {asin}): {e}")
        raise

    # Extract title (required field)
    title = await safe_extract_text(page, AmazonSelectors.TITLE)
    if not title:
        logger.warning(f"Title not found for ASIN {asin} at {url}")
        return None

    # Extract price information
    price_str = await safe_extract_text(page, AmazonSelectors.PRICE)
    price = parse_price(price_str)
    currency = parse_currency(price_str)

    list_price_str = await safe_extract_text(page, AmazonSelectors.LIST_PRICE)
    list_price = parse_price(list_price_str)

    # Validate list price is actually higher than current price
    if list_price and price and list_price <= price:
        list_price = None

    # Extract discount percentage
    discount_percentage = None
    main_price_block = await page.query_selector(AmazonSelectors.PRICE_CONTAINERS)
    if main_price_block:
        discount_elem = await main_price_block.query_selector(
            AmazonSelectors.DISCOUNT_PERCENTAGE
        )
        if discount_elem:
            discount_str = (await discount_elem.inner_text()).strip()
            discount_percentage = parse_discount(discount_str)

    # Extract rating
    rating = None
    rating_str = await safe_extract_text(page, AmazonSelectors.RATING)
    if rating_str:
        match = re.search(r"([\d.]+)", rating_str)
        if match:
            rating = float(match.group(1))

    # Extract review count
    reviews_count = None
    reviews_str = await safe_extract_text(page, AmazonSelectors.REVIEWS_COUNT)
    if reviews_str:
        clean_reviews = re.sub(r"[^\d]", "", reviews_str)
        if clean_reviews:
            reviews_count = int(clean_reviews)

    # Check Prime eligibility
    is_prime = False
    for sel in AmazonSelectors.PRIME_LOGO:
        if await page.query_selector(sel):
            is_prime = True
            break

    # Extract best sellers rank
    best_sellers_rank = await safe_extract_text(page, AmazonSelectors.BEST_SELLERS_RANK)
    if best_sellers_rank:
        best_sellers_rank = " ".join(best_sellers_rank.split())

    # Extract bullet points (product features)
    bullet_points: list[str] = []
    bullet_elements = await page.query_selector_all(AmazonSelectors.BULLET_POINTS[0])
    for elem in bullet_elements:
        text = (await elem.inner_text()).strip()
        if text and len(bullet_points) < 5:
            bullet_points.append(text)

    # Extract main product image
    main_image_url = None
    for sel in AmazonSelectors.MAIN_IMAGE:
        img_element = await page.query_selector(sel)
        if img_element:
            main_image_url = await img_element.get_attribute("src")
            break

    return {
        "asin": asin,
        "title": title,
        "rank": rank,
        "price": price,
        "currency": currency,
        "list_price": list_price,
        "discount_percentage": discount_percentage,
        "rating": rating,
        "reviews_count": reviews_count,
        "is_prime": is_prime,
        "best_sellers_rank": best_sellers_rank,
        "bullet_points": bullet_points,
        "main_image_url": main_image_url,
    }


async def parse_category_full(category_url: str) -> list[dict]:
    """
    Complete workflow: scrape category page, then parse all product pages.
    Returns list of product data dictionaries.
    """
    # Step 1: Get product URLs from category
    urls = await get_top_5_product_url(category_url)
    parsed_products: list[dict[str, Any]] = []

    if not urls:
        logger.warning("No product URLs found")
        return parsed_products

    logger.info(f"Starting to parse {len(urls)} products...")

    # Step 2: Parse each product page
    async with get_browser_context() as context:
        # Initialize session with US location
        init_page = await context.new_page()
        await inject_stealth(init_page)
        await init_page.goto("https://www.amazon.com", wait_until="domcontentloaded")
        await set_us_location(init_page)
        await init_page.close()

        # Parse each product in separate page
        for rank, url in enumerate(urls, start=1):
            page = await context.new_page()
            await inject_stealth(page)

            try:
                data = await parse_product_page(page, url, rank)
                if data and data["asin"]:
                    parsed_products.append(data)
            except Exception as e:
                logger.error(f"Failed to parse {url}: {e}")
            finally:
                await page.close()

    logger.info(f"Successfully parsed {len(parsed_products)} products")
    return parsed_products
