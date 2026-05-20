from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def scrape_reliance(query):
    options = Options()
    options.add_argument("--headless=new")  # Optional: uncomment for headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        search_term = query.replace(" ", "%20")
        url = f"https://www.reliancedigital.in/products?q={search_term}&page_no=1&page_size=12&page_type=number"
        driver.get(url)

        # Close popup if it appears
        try:
            # Handle popup if present
            no_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Yes, Notify me')]"))
            )
            no_button.click()
            print("Popup closed")
            time.sleep(2)
        except:
            print("No popup appeared")

        # Scroll slightly
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract product data from JSON-LD
        script_tags = soup.find_all("script", {"type": "application/ld+json"})
        products = []

        for script in script_tags:
            try:
                data = json.loads(script.string)
                if data.get("@type") == "ItemList":
                    for idx, item in enumerate(data.get("itemListElement", [])):
                        if idx >= 3:
                            break

                        name = item.get("name")
                        url_part = item.get("url")
                        link = "https://" + url_part.replace("&#x2F;", "/") if url_part else None

                        # Use index to map to price blocks
                        price_divs = soup.select("div.price-container .price")
                        price = price_divs[idx].get_text(strip=True) if idx < len(price_divs) else "N/A"

                        products.append({
                            "title": name,
                            "price": price,
                            "link": link
                        })
                    break
            except Exception as e:
                continue

        driver.quit()
        print("Reliance Digital products found:", len(products))
        return products

    except Exception as e:
        print("Reliance scraping failed:", e)
        driver.quit()
        return []
