from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scraper.amazon import scrape_amazon
from scraper.flipkart import scrape_flipkart
from scraper.croma import scrape_croma
from scraper.reliance import scrape_reliance
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def add_value_tag(scraped_data: dict) -> dict:
    # Collect all prices along with their platform and index for tagging later
    all_prices = []

    for platform, items in scraped_data.items():
        for idx, item in enumerate(items):
            price_str = item.get("price", "").replace("₹", "").replace(",", "").replace(".00","").strip()
            if price_str.isdigit():
                all_prices.append((int(price_str), platform, idx))
    if not all_prices:
        return scraped_data

    # Determine min and max prices
    min_price = min(all_prices, key=lambda x: x[0])[0]
    max_price = max(all_prices, key=lambda x: x[0])[0]

    # Tag items based on price
    for price, platform, idx in all_prices:
        if price == min_price:
            scraped_data[platform][idx]["value_tag"] = "✅ Best Value"
        elif price == max_price:
            scraped_data[platform][idx]["value_tag"] = "🚩 Overpriced"
        else:
            scraped_data[platform][idx]["value_tag"] = "⚖️ Fair Deal"
    return scraped_data

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def run_blocking_tasks(q: str):
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, scrape_amazon, q),
            loop.run_in_executor(executor, scrape_flipkart, q),
            loop.run_in_executor(executor, scrape_croma, q),
            loop.run_in_executor(executor, scrape_reliance, q),
        ]
        return futures

@app.get("/search")
async def search_product(q: str):
    results = await asyncio.gather(*run_blocking_tasks(q))
    result_dict = {
        "amazon": results[0],
        "flipkart": results[1],
        "croma": results[2],
        "reliance": results[3],
    }
    tagged_results = add_value_tag(result_dict)
    return JSONResponse(content=tagged_results)
