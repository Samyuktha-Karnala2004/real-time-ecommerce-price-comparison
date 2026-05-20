from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_croma(query):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Format query for URL
        query_param = query.replace(" ", "%20")
        url = f"https://www.croma.com/searchB?q={query_param}%3Arelevance&text={query_param}"
        driver.get(url)
        time.sleep(3)

        # Scroll to load all products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        cards = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
        print("Croma products found:", len(cards))

        products = []

        for card in cards:
            try:
                # Title
                try:
                    title = card.find_element(By.CSS_SELECTOR, ".product-title").text.strip()
                except:
                    title = None

                # Link
                try:
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    link = None

                # Price
                try:
                    price = card.find_element(By.CSS_SELECTOR, ".amount").text.strip()
                except:
                    price = "N/A"

                if title and link:
                    products.append({
                        "title": title,
                        "price": price,
                        "link": link
                    })

                if len(products) >= 3:
                    break

            except Exception as e:
                print("Skipping product due to:", e)
                continue

        driver.quit()
        return products

    except Exception as e:
        print("Croma scraping failed:", e)
        driver.quit()
        return []
