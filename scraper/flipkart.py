from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_flipkart(query):
    options = Options()
    # Disable headless for now to see what happens
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(2)

        # Close login popup
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
            )
            close_btn.click()
        except:
            pass

        # Wait for grid tiles (a[contains href=/p/])
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/p/')]"))
        )

        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        print("Flipkart products found:", len(links))

        items = []
        for link in links:
            try:
                product_url = link.get_attribute("href")
                title = link.text.strip()

                # XPath logic to find price within same tile
                price_elem = link.find_element(By.XPATH, ".//following::div[contains(text(),'₹')]")
                price = price_elem.text.strip()

                if title and price:
                    items.append({
                        "title": title,
                        "price": price,
                        "link": product_url
                    })

                if len(items) >= 3:
                    break
            except Exception as e:
                print("Parsing error:", e)
                continue

        driver.quit()
        return items

    except Exception as e:
        driver.quit()
        print("Flipkart scrape failed:", e)
        return []



