import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--headless")

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

def get_text(url_info):
    category, url = url_info
    try:
        r = session.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')

        paragraphs = soup.find_all('p', class_='topic-body__content-text')
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return {'Category': category, 'Text': text} if len(text) > 100 else None
    except: return None

categories = {
    'ussr':'https://lenta.ru/rubrics/ussr/',
    'forces':'https://lenta.ru/rubrics/forces/',
    'wellness':'https://lenta.ru/rubrics/wellness/',
    'economy': 'https://lenta.ru/rubrics/economics/',
    'sport': 'https://lenta.ru/rubrics/sport/',
    'tourism':'https://lenta.ru/rubrics/travel/',
    'science':'https://lenta.ru/rubrics/science/'
}

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
all_links = []

try:
    for cat, link in categories.items():
        driver.get(link)
        time.sleep(4)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(100): 
    
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            driver.execute_script("window.scrollBy(0, -1000);")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/news/'], a[href*='/articles/']")
            print(f"[{cat}] Шаг {i+1}: Собрано {len(links)} ссылок...", end='\r')
            
            if new_height == last_height and i > 10: break
            last_height = new_height

        final_links = list(set([el.get_attribute('href') for el in links if 'lenta.ru' in el.get_attribute('href')]))
        for fl in final_links:
            all_links.append((cat, fl))

finally:
    driver.quit()

print(f"\nВсего ссылок: {len(all_links)}. Начинаю загрузку контента...")

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(get_text, all_links))
    data = [r for r in results if r]

pd.DataFrame(data).to_csv('LentaRu_pars.csv', index=False, encoding='utf-8-sig')
print(f"Готово! Сохранено {len(data)} статей.")




