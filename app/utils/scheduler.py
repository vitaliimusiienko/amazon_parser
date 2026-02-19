import logging
import asyncio
from app.services.amazon_parser import parse_categories_page, get_browser_context
from app.db.session import AsyncSessionLocal
from app.services.category_service import get_or_create_category

logger = logging.getLogger(__name__)

async def sync_amazon_categories():
    """
    Фоновая задача: собирает только корневые категории с главной страницы Best Sellers.
    """
    logger.info("Запуск ежедневной синхронизации КОРНЕВЫХ категорий Amazon...")
    main_url = "https://www.amazon.com/gp/bestsellers"
    
    try:
        async with get_browser_context() as context:
            page = await context.new_page()
            
            # ШАГ 1: Берем только список с главной страницы
            roots = await parse_categories_page(page, main_url)
            
            if not roots:
                logger.error("Не удалось получить корневые категории. Проверь селекторы или капчу.")
                return
            
            logger.info(f"Найдено {len(roots)} корневых категорий. Начинаем сохранение...")
            
            # ШАГ 2: Сразу сохраняем в базу (без проваливания внутрь)
            async with AsyncSessionLocal() as db:
                for cat in roots:
                    await get_or_create_category(
                        db=db,
                        category_url=cat['url'],
                        category_name=cat['name']
                    )
            
            logger.info(f"Синхронизация успешно завершена. Сохранено {len(roots)} категорий.")

    except Exception as e:
        logger.error(f"Критическая ошибка в планировщике категорий: {e}", exc_info=True)