# Universal AI Image Scraper 🧠🕷️

An intelligent, CAPTCHA-bypassing image scraper that uses the DuckDuckGo API and Google Gemini AI to dynamically analyze topics, generate precise search queries, and automatically filter out irrelevant junk.

## 🌟 Why is this better than traditional scrapers?
Traditional scrapers (like Selenium + Google Images) constantly break, get blocked by CAPTCHAs, or pull completely irrelevant images. 

**Universal AI Scraper** solves this by:
1. **Bypassing CAPTCHAs:** It hits the native DuckDuckGo hidden API directly. No browsers, no Selenium, no blocks.
2. **AI Topic Analysis:** Before searching, Gemini AI analyzes your topic and generates hyper-optimized search strings.
3. **Smart Auditing:** Gemini automatically builds a list of "Negative Keywords" for your topic (e.g. if you search for an anime character, it blocks "cosplay", "t-shirt", "toy"). The Python script then instantly purges any image metadata containing those bad words.

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/udaydomadiya08/universal-ai-scraper.git
cd universal-ai-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Usage

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/) and set it as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Run the scraper:
```bash
python scraper.py
```

### Example Code
You can easily import and use the scraper in your own Python projects:

```python
import asyncio
from scraper import UniversalImageScraper

async def main():
    scraper = UniversalImageScraper(gemini_api_key="YOUR_KEY")
    
    # The AI will automatically avoid pulling hardware store listings!
    await scraper.scrape("A rusty wrench aesthetic", count=20)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📜 License
MIT License
