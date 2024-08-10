import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.db_utils import create_crud_functions
from openai_utils.openai_base import opanai_returns_formatted_ebay_demand_data
import urllib.parse
import diskcache as dc
from concurrent.futures import ThreadPoolExecutor, as_completed

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    return driver

cache = dc.Cache(os.path.join(os.path.dirname(__file__), 'ebay_cache'))

def scrape_ebay_demand_el(item_search_url):
    driver = setup_driver()
    
    driver.get(item_search_url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "srp-results"))
        )
    except Exception as e:
        print(f"Timeout waiting for eBay search results for item {item_search_url}: {e}")
        return None
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    try:
        results_list = soup.find("ul", class_="srp-results srp-list clearfix").get_text()
        return results_list
    except AttributeError as e:
        print(f"Error processing eBay search results for item {item_search_url}: {e}")
        return None
    finally:
        driver.quit()

def create_search_string(item_data):
    columns_to_concat = ["ASIN", "Description", "FNSku", "Product", "UPC"]
    search_string = ' '.join(str(item_data.get(col, '')) for col in columns_to_concat if item_data.get(col))
    return search_string

def get_formatted_ebay_items(url):
    if url in cache:
        return cache[url]
    ebay_demand_el = scrape_ebay_demand_el(url)
    formatted_ebay_items = opanai_returns_formatted_ebay_demand_data(ebay_demand_el)
    cache[url] = formatted_ebay_items
    return formatted_ebay_items

def process_item(item, search_string, ebay_demand_crud):
    if search_string == '':
        print(f"No search string found for item {item[0]}")
        return

    encoded_search_string = urllib.parse.quote(search_string)
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_search_string}&LH_Sold=1&LH_Complete=1"

    print(f"Formatting eBay demand data for item {search_string}")
    formatted_ebay_items = get_formatted_ebay_items(search_url)
    
    print(f"Inserting eBay demand data for item {search_string}")
    for ebay_item in formatted_ebay_items:
        ebay_item['item_id'] = item[0]
        ebay_item['auction_id'] = item[1]
        ebay_item['url'] = search_url
        ebay_item['search_string'] = search_string
        ebay_demand_crud['insert'](ebay_item)

def main(max_items_to_process=None):
    items_crud = create_crud_functions('items_data')
    ebay_demand_crud = create_crud_functions('ebay_demand_data')

    items = items_crud['get_all']()
    
    if max_items_to_process:
        items = items[:max_items_to_process]

    processed_search_strings = set()
    
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        
        for item in items:
            item_data = json.loads(item[2])
            search_string = create_search_string(item_data)
            
            if search_string and search_string not in processed_search_strings:
                processed_search_strings.add(search_string)
                futures.append(executor.submit(process_item, item, search_string, ebay_demand_crud))
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing item: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Process interrupted by user.")
