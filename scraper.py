"""
Universal AI Image Scraper
An intelligent, CAPTCHA-bypassing image scraper that uses DuckDuckGo and Google Gemini
to dynamically analyze topics, generate precise queries, and automatically filter out irrelevant results.
"""

import os
import json
import asyncio
import aiohttp
from duckduckgo_search import DDGS
import google.generativeai as genai

class UniversalImageScraper:
    def __init__(self, gemini_api_key: str, output_dir: str = "downloads"):
        if not gemini_api_key:
            raise ValueError("A Gemini API key is required. Get one at: https://aistudio.google.com/")
        
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def analyze_topic(self, topic: str) -> dict:
        """Uses AI to generate optimized search terms and negative keywords."""
        print(f"🧠 [AI] Analyzing topic: '{topic}'...")
        prompt = f"""
        You are an expert search engine optimizer preparing an image search for: '{topic}'.
        
        Provide a JSON configuration with:
        1. "core_subject": The main subject.
        2. "positive_keywords": 5-10 words that strongly identify good results.
        3. "negative_keywords": 10-20 words that identify bad/irrelevant results (e.g. diagrams, memes, commercial products, cosplays, unrelated news).
        4. "search_queries": 3 Highly precise search strings for DuckDuckGo. E.g. "{topic} high quality photo".
        
        Return ONLY valid JSON.
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = response.text
            # Extract JSON block
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            spec = json.loads(text.strip())
            print(f"   => Optimized Query: {spec['search_queries'][0]}")
            return spec
        except Exception as e:
            print(f"⚠️ AI Analysis failed: {e}. Falling back to default query.")
            return {"search_queries": [topic], "negative_keywords": []}

    def fetch_image_metadata(self, query: str, max_results: int = 50) -> list:
        """Bypasses CAPTCHAs by using the native DuckDuckGo API."""
        print(f"🔍 [DDGS] Searching for: '{query}'...")
        candidates = []
        try:
            with DDGS() as ddgs:
                results = ddgs.images(
                    query,
                    region="wt-wt",
                    safesearch="off",
                    size="Wallpaper",
                    type_image="photo",
                    max_results=max_results
                )
                for r in results:
                    if 'image' in r:
                        candidates.append({
                            "url": r['image'],
                            "title": r.get('title', ''),
                            "source": r.get('source', '')
                        })
        except Exception as e:
            print(f"❌ DDGS API failed: {e}")
        
        print(f"   => Scraped {len(candidates)} raw images.")
        return candidates

    def local_filter(self, candidates: list, negatives: list) -> list:
        """Instantly drops any images whose metadata matches negative keywords."""
        approved = []
        negatives = [n.lower() for n in negatives]
        
        for item in candidates:
            text_block = f"{item['title']} {item['source']}".lower()
            
            # Check against negative keywords
            is_bad = any(neg in text_block for neg in negatives)
            if not is_bad:
                approved.append(item['url'])
                
        print(f"🛡️  [Filter] Kept {len(approved)} out of {len(candidates)} images.")
        return approved

    async def _download_file(self, session: aiohttp.ClientSession, url: str, index: int, topic_dir: str):
        """Asynchronously downloads a single image."""
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    content = await response.read()
                    ext = url.split('.')[-1][:4] if '.' in url else 'jpg'
                    if not ext.isalnum(): ext = 'jpg'
                    
                    filename = os.path.join(topic_dir, f"img_{index:04d}.{ext}")
                    with open(filename, 'wb') as f:
                        f.write(content)
                    return True
        except Exception:
            pass
        return False

    async def download_images(self, urls: list, topic: str):
        """Downloads all approved URLs concurrently."""
        topic_dir = os.path.join(self.output_dir, topic.replace(" ", "_"))
        os.makedirs(topic_dir, exist_ok=True)
        
        print(f"⬇️  [Download] Downloading {len(urls)} images to {topic_dir}...")
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [self._download_file(session, url, i, topic_dir) for i, url in enumerate(urls)]
            results = await asyncio.gather(*tasks)
            
        success_count = sum(1 for r in results if r)
        print(f"✅  Successfully downloaded {success_count}/{len(urls)} images!")

    async def scrape(self, topic: str, count: int = 20):
        """Main execution pipeline."""
        print(f"\n{'='*50}\nSTARTING SCRAPE: {topic}\n{'='*50}")
        
        # 1. AI Analysis
        spec = await self.analyze_topic(topic)
        query = spec['search_queries'][0]
        
        # 2. Native DDGS Search
        candidates = self.fetch_image_metadata(query, max_results=count + 15)
        
        if not candidates:
            return
            
        # 3. Local Auditing
        approved_urls = self.local_filter(candidates, spec.get('negative_keywords', []))
        
        # 4. Download
        await self.download_images(approved_urls[:count], topic)

if __name__ == "__main__":
    # Example usage
    API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
    
    scraper = UniversalImageScraper(gemini_api_key=API_KEY)
    
    # Run a test
    topic_to_scrape = "Cyberpunk Tokyo street aesthetic"
    asyncio.run(scraper.scrape(topic_to_scrape, count=10))
