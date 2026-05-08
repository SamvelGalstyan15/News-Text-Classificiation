import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


chrome_options = Options()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    "Connection": "keep-alive"
}

def func(url):
    try:
        if url.startswith('/'):
            url = "https://ria.ru" + url

        req = requests.get(url, headers=headers, timeout=10)
        if req.status_code != 200: 
            return ""        
        soup = BeautifulSoup(req.text, 'lxml')
        blocks = soup.find_all('div', class_='article__block', attrs={"data-type": "text"})        
        if blocks:
            return " ".join(b.get_text(" ", strip=True) for b in blocks)
        
        article_body = soup.find('div', class_='article__text')
        if article_body:
            return article_body.get_text(" ", strip=True)
            
        return ""
    except Exception as ex:
        print(ex)
        return ""

categories = {
    'economy':'https://ria.ru/economy/',
    'sport':'https://ria.ru/sport/',
    'tourism':'https://ria.ru/tourism/',
    'science':'https://ria.ru/science/',

}
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

data = []

for category,link in categories.items():
    driver.get(link)

    scroll_count = 5 
    for i in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) 

    links_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='ria.ru']")

    all_links = []
    for i in links_elements:
        href = i.get_attribute('href')
        if href and href.endswith('.html') and '/20' in href: 
            all_links.append(href)
        time.sleep(1)

    all_links = list(set(all_links)) 
    print(f"Найдено ссылок после прокрутки: {len(all_links)}")
   
    for j in all_links:
        text = func(j)
        if text and len(text) > 50:
            data.append({
                    'Category' : category,
                    'Text'  :  text

            })
     
driver.quit() 

df = pd.DataFrame(data)

df.to_csv('Ria_pars.csv')
