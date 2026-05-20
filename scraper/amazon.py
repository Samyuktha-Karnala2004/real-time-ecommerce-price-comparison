from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def scrape_amazon(query):
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
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(3)

        # Scroll to the bottom to trigger all lazy-loaded products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        print("Amazon products found:", len(cards))

        products = []

        for card in cards:
            try:
                # --- TITLE ---
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2 span").text.strip()
                except:
                    title = None

                # --- LINK ---
                try:
                    link = card.find_element(By.XPATH,
                                             ".//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']").get_attribute(
                        "href")
                except:
                    try:
                        link = card.find_element(By.XPATH, ".//a[contains(@href, '/dp/')]").get_attribute("href")
                    except:
                        link = None

                # --- PRICE ---
                try:
                    price = card.find_element(By.XPATH, ".//span[@class='a-price']").text.replace("\n", ".")
                except:
                    try:
                        price = card.find_element(By.CLASS_NAME, "a-offscreen").text
                    except:
                        price = None

                if title and link:
                    products.append({
                        "title": title,
                        "price": price if price else "N/A",
                        "link": link
                    })

                if len(products) >= 3:
                    break

            except Exception as e:
                print("Skipping card due to error:", e)
                continue

        driver.quit()
        return products

    except Exception as e:
        print("Amazon scraping failed:", e)
        driver.quit()
        return []

