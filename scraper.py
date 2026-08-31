import asyncio
import logging
from typing import List, Dict, Any, Callable, Optional
from playwright.async_api import async_playwright
from playwright_stealth import stealth
from database import DatabaseManager

class AdvancedScraper:
    def __init__(self, concurrency: int = 3):
        self.concurrency = concurrency
        self.db = DatabaseManager()

    async def _scrape_page(self, context, url: str) -> Dict[str, Any]:
        page = await context.new_page()
        await stealth(page)
        
        result = {"url": url, "title": "N/A", "price": "N/A", "status": "ÉCHEC"}

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            
            if response and response.status == 200:
                await page.evaluate("window.scrollBy(0, 300)")
                await asyncio.sleep(0.5)

                title = await page.title()
                
                # Recherche d'éléments de prix
                price_elem = await page.query_selector(".price, .a-price, [data-test='product-price'], span:has-text('€')")
                price = await price_elem.inner_text() if price_elem else "Non trouvé"

                result.update({
                    "title": title[:40].strip() if title else "Sans titre",
                    "price": price.strip().replace("\n", " "),
                    "status": "SUCCÈS"
                })

        except Exception as e:
            logging.error(f"Erreur sur {url}: {str(e)}")
            result["status"] = "TIMEOUT/BLOCAGE"
        finally:
            await page.close()

        # Sauvegarde immédiate
        self.db.save_product(result)
        return result

    async def run(self, urls: List[str], real_time_callback: Optional[Callable[[Dict[str, Any], float], None]] = None):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )

            semaphore = asyncio.Semaphore(self.concurrency)

            async def sem_task(url: str):
                async with semaphore:
                    return await self._scrape_page(context, url)

            tasks = [sem_task(u) for u in urls]
            total = len(tasks)

            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                item = await task
                progress = (i / total) * 100
                if real_time_callback:
                    real_time_callback(item, progress)

            await browser.close()
