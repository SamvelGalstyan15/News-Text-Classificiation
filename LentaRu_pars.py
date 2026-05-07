# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import pandas as pd


# chrome_options = Options()
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
#     "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
#     "Connection": "keep-alive"
# }


# session = requests.Session()
# session.headers.update(headers)

# def func(url):
#     try:
#         req = session.get(url, timeout=10)
#         if req.status_code != 200: return "" 
#         soup = BeautifulSoup(req.text, 'lxml')
        
#         # Самый надежный селектор для Lenta.ru
#         content = soup.find('div', {'itemprop': 'articleBody'})
#         if content:
#             paragraphs = content.find_all('p')
#             return " ".join(p.get_text(strip=True) for p in paragraphs)
#         return ""
#     except Exception as ex:
#         return ""


# categories = {
#     'ussr':'https://lenta.ru/rubrics/ussr/',
#     'forces':'https://lenta.ru/rubrics/forces/',
#     'wellness':'https://lenta.ru/rubrics/wellness/',
#     'economy': 'https://lenta.ru/rubrics/economics/',
#     'sport': 'https://lenta.ru/rubrics/sport/',
#     'tourism':'https://lenta.ru/rubrics/travel/',
#     'science':'https://lenta.ru/rubrics/science/'

# }

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# data = []

# for category,link in categories.items():
#     driver.get(link)

#     scroll_count = 10 
#     for i in range(scroll_count):
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2) 

#     links_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/news/'], a[href*='/articles/']")

#     all_links = []
#     for i in links_elements:
#         href = i.get_attribute('href')
#         if href: 
#             all_links.append(href)
#         # time.sleep(0,5)

#     all_links = list(set(all_links)) 
#     print(f"Найдено ссылок после прокрутки: {len(all_links)}")
   
#     for j in all_links:
#         text = func(j)
#         if text and len(text) > 50:
#             data.append({
#                     'Category' : category,
#                     'Text'  :  text

#             })
     
# driver.quit() 

# df = pd.DataFrame(data)

# df.to_csv('LentaRu_pars.csv')


# 2
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
# chrome_options.add_argument("--headless") # Раскомментируйте, чтобы скрыть окно

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

def get_text(url_info):
    category, url = url_info
    try:
        r = session.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        # Самый точный селектор по вашему скриншоту:
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
        # Для ТЫСЯЧ статей нужно минимум 100-150 итераций
        for i in range(100): 
            # Листаем вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            # "Дергаем" вверх, чтобы сработал JS-триггер подгрузки
            driver.execute_script("window.scrollBy(0, -1000);")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Считаем ссылки в процессе
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


# # 3


# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# # Настройки браузера
# chrome_options = Options()
# # chrome_options.add_argument("--headless") # Фоновый режим для скорости
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# def get_full_text(url):
#     """Собирает текст статьи через драйвер (надежнее, чем requests)"""
#     try:
#         driver.execute_script("window.open('');") # Открываем новую вкладку
#         driver.switch_to.window(driver.window_handles[1])
#         driver.get(url)
#         time.sleep(1.5)
        
#         # Универсальный поиск параграфов
#         elements = driver.find_elements(By.CSS_SELECTOR, "p")
#         text = " ".join([el.text for el in elements if len(el.text) > 50])
        
#         driver.close() # Закрываем вкладку
#         driver.switch_to.window(driver.window_handles[0])
#         return text
#     except:
#         return ""

# categories = {
#     'ussr':'https://lenta.ru/rubrics/ussr/',
#     'forces':'https://lenta.ru/rubrics/forces/',
#     'wellness':'https://lenta.ru/rubrics/wellness/',
#     'economy': 'https://lenta.ru/rubrics/economics/',
#     'sport': 'https://lenta.ru/rubrics/sport/',
#     'tourism':'https://lenta.ru/rubrics/travel/',
#     'science':'https://lenta.ru/rubrics/science/'
# }


# data = []

# for category, link in categories.items():
#     print(f"Обработка категории: {category}")
#     driver.get(link)
    
#     # ПРАВИЛЬНЫЙ СКРОЛЛИНГ: небольшими шагами
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     for _ in range(10): # 10 итераций скролла
#         driver.execute_script("window.scrollBy(0, 1000);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height: break # Если контент кончился
#         last_height = new_height

#     # Собираем все ссылки на новости и статьи
#     links_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/news/'], a[href*='/articles/']")
#     all_links = list(set([el.get_attribute('href') for el in links_elements]))
    
#     print(f"Найдено уникальных ссылок: {len(all_links)}")

#     for url in all_links:
#         article_text = get_full_text(url)
#         if len(article_text) > 100:
#             data.append({'Category': category, 
#                         'Text': article_text})

# driver.quit()
# df = pd.DataFrame(data)
# df.to_csv('LentaRu_pars.csv', index=False)
# print("Готово!")




# 4

# import time
# import re
# import pandas as pd
# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# # --- НАСТРОЙКИ ---
# LIMIT_PER_CATEGORY = 400
# DAYS_TO_SCAN = 90

# # Ключевое слово в ссылке : Название для CSV
# categories_map = {
#     'ussr':'https://lenta.ru/rubrics/ussr/',
#     'forces':'https://lenta.ru/rubrics/forces/',
#     'wellness':'https://lenta.ru/rubrics/wellness/',
#     'economy': 'https://lenta.ru/rubrics/economics/',
#     'sport': 'https://lenta.ru/rubrics/sport/',
#     'tourism':'https://lenta.ru/rubrics/travel/',
#     'science':'https://lenta.ru/rubrics/science/'
# }


# def clean_text(text):
#     if not text: return ""
#     text = re.sub(r'[a-zA-Z0-9,\.\-\–\—\«\»\"\"\/\:\%]', ' ', text)
#     text = re.sub(r'\b[а-яёА-ЯЁ]\b', ' ', text)
#     return re.sub(r'\s+', ' ', text).lower().strip()

# chrome_options = Options()
# # Если ERR_NAME_NOT_RESOLVED повторяется, уберите headless, чтобы видеть, что происходит
# # chrome_options.add_argument("--headless") 

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# data = []
# stats = {name: 0 for name in categories_map.values()}
# current_date = datetime(2025, 2, 18) # Фикс даты

# try:
#     for _ in range(DAYS_TO_SCAN):
#         date_path = current_date.strftime('%Y/%m/%d')
#         archive_url = f"https://lenta.ru{date_path}/"
        
#         print(f"\n--- Дата: {date_path} ---")
#         try:
#             driver.get(archive_url)
#             time.sleep(3)
            
#             links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/news/"], a[href*="/articles/"]')
#             urls = list(set([el.get_attribute('href') for el in links if el.get_attribute('href')]))
            
#             for url in urls:
#                 # Определяем категорию
#                 found_cat = None
#                 for slug, formal_name in categories_map.items():
#                     if f"/{slug}/" in url.lower():
#                         if stats[formal_name] < LIMIT_PER_CATEGORY:
#                             found_cat = formal_name
#                         break
                
#                 if found_cat:
#                     driver.get(url)
#                     time.sleep(1.5)
#                     ps = driver.find_elements(By.CSS_SELECTOR, 'p') # Простой селектор
#                     text = " ".join([p.text for p in ps if len(p.text) > 40])
                    
#                     cleaned = clean_text(text)
#                     if len(cleaned) > 300:
#                         data.append({'Category': found_cat, 'Text': cleaned})
#                         stats[found_cat] += 1
#                         print(f"  [+] {found_cat}: {stats[found_cat]}")
                    
#                     driver.back()
#                     time.sleep(1)

#         except Exception as e:
#             print(f" Ошибка доступа к {date_path}. Проверьте VPN/Интернет.")
#             time.sleep(5)
            
#         if all(count >= LIMIT_PER_CATEGORY for count in stats.values()):
#             break
#         current_date -= timedelta(days=1)

# finally:
#     driver.quit()
#     if data:
#         pd.DataFrame(data).to_csv('LentaRu_pars.csv', index=False, encoding='utf-8-sig')
#         print("Готово!")



