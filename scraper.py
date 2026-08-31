import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

class AdvancedScraper:
    def __init__(self, max_concurrency=3, **kwargs):
        self.max_concurrency = max_concurrency

    async def _scrape_page(self, context, url, semaphore):
        async with semaphore:
            page = await context.new_page()
            
            # Masquage basique du webdriver
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            data = {
                "url": url,
                "title": None,
                "price": None,
                "status": "Erreur",
                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # Navigation vers l'URL
                response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                
                if response and response.status == 200:
                    # Extraction du titre
                    title_element = await page.query_selector("h1")
                    if title_element:
                        data["title"] = (await title_element.inner_text()).strip()
                    else:
                        data["title"] = await page.title()
                        
                    # Extraction indicative du prix (sélecteurs courants)
                    price_element = await page.query_selector("[class*='price'], [id*='price'], .amount")
                    if price_element:
                        data["price"] = (await price_element.inner_text()).strip()
                    
                    data["status"] = "Succès"
                else:
                    data["status"] = f"Échec (HTTP {response.status if response else 'No Response'})"
                    
            except Exception as e:
                data["status"] = f"Erreur: {str(e)}"
            finally:
                await page.close()
                return data

    async def run(self, urls):
        return await self.scrape_urls(urls)

    async def scrape_batch(self, urls):
        return await self.scrape_urls(urls)

    async def scrape_urls(self, urls):
        async with async_playwright() as p:
            # Lancement du navigateur Chromium en mode headless
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            
            semaphore = asyncio.Semaphore(self.max_concurrency)
            tasks = [self._scrape_page(context, url, semaphore) for url in urls]
            results = await asyncio.gather(*tasks)
            
            await context.close()
            await browser.close()
            return results
