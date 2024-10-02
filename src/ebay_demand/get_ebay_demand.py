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
import random
import string

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.db_utils import create_crud_functions
from openai_utils.openai_base import opanai_returns_formatted_ebay_demand_data
import urllib.parse
import diskcache as dc
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--tor")
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    return driver


ebay_demand_el_cache = dc.Cache(os.path.join(os.path.dirname(__file__), 'ebay_demand_el_cache'))

def scrape_ebay_demand_el(item_search_url):
    if item_search_url in ebay_demand_el_cache:
        return ebay_demand_el_cache[item_search_url]

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
        ebay_demand_el = soup.find("ul", class_="srp-results srp-list clearfix").get_text()

        if not ebay_demand_el:
            raise ValueError(f"No results found for item {item_search_url}")

        ebay_demand_el_cache[item_search_url] = ebay_demand_el
        return ebay_demand_el
    except AttributeError as e:
        print(f"Error processing eBay search results for item {item_search_url}: {e}")
        return None
    finally:
        driver.quit()

def create_search_string(item_data):
    columns_to_concat = ["ASIN", "Description", "FNSku", "Product", "UPC", "Make", "Model"]
    search_string = ' '.join(str(item_data.get(col, '')) for col in columns_to_concat if item_data.get(col))
    return search_string

def format_and_save_ebay_demand_items(ebay_demand_el, ebay_demand_crud, item, search_url, search_string):
    formatted_ebay_items = opanai_returns_formatted_ebay_demand_data(ebay_demand_el)
    # print(f"Inserting eBay demand data for item {item}")
    for ebay_item in formatted_ebay_items:
        ebay_item['item_id'] = item[0]
        ebay_item['auction_id'] = item[1]
        ebay_item['url'] = search_url
        ebay_item['search_string'] = search_string
        ebay_demand_crud['insert'](ebay_item)

def process_item_og(item, search_string, ebay_demand_crud):
    if search_string == '':
        print(f"No search string found for item {item[0]}")
        return

    encoded_search_string = urllib.parse.quote(search_string)
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_search_string}&LH_Sold=1&LH_Complete=1"

    if search_url == "https://www.ebay.com/sch/i.html?_nkw=%20&LH_Sold=1&LH_Complete=1":
        print(f"Skipping item {item[0]} due to empty search string")
        return

    print(f"Auction ID: {item[1]} - Formatting eBay demand data for item {search_string}")
    ebay_demand_el = scrape_ebay_demand_el(search_url)

    # Start a new thread to format and save eBay demand items
    threading.Thread(target=format_and_save_ebay_demand_items, args=(ebay_demand_el, ebay_demand_crud, item, search_url, search_string)).start()

    # Return immediately
    return


def main(max_items_to_process=None):
    items_crud = create_crud_functions('items_data')
    ebay_demand_crud = create_crud_functions('ebay_demand_data')

    items = items_crud['get_all']()
    
    if max_items_to_process:
        items = items[:max_items_to_process]

    processed_search_strings = set()
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = []
        
        for item in items:
            item_data = json.loads(item[2])
            search_string = create_search_string(item_data)
            
            if search_string and search_string not in processed_search_strings:
                processed_search_strings.add(search_string)
                futures.append(executor.submit(process_item_og, item, search_string, ebay_demand_crud))
        
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

def generate_random_id(length=16):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def fetch_ebay_demand(items_data):
    print(f"Fetching eBay demand data for items: {items_data}")
    
    ebay_demand_data = []
    
    def process_item(item):
        try:
            search_string = create_search_string(item)
            
            if search_string:
                search_url = f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote(search_string)}&LH_Sold=1&LH_Complete=1"
                print(f"Getting eBay demand data for {search_url}")
                
                ebay_demand_el = scrape_ebay_demand_el(search_url)
                
                if ebay_demand_el:
                    formatted_ebay_items = opanai_returns_formatted_ebay_demand_data(ebay_demand_el)
                    
                    for ebay_item in formatted_ebay_items:
                        ebay_item['id'] = generate_random_id()
                        ebay_item['item_id'] = item['id']
                        ebay_item['auction_id'] = item['auction_id']
                        ebay_item['url'] = search_url
                        ebay_item['search_string'] = search_string
                        ebay_demand_data.append(ebay_item)
        except Exception as e:
            print(f"Error processing item {item}: {e}")

    try:
        with ThreadPoolExecutor(max_workers=17) as executor:
            futures = [executor.submit(process_item, item) for item in items_data]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in future: {e}")
        
        return ebay_demand_data
    
    except Exception as e:
        print(f"Error fetching eBay demand data: {e}")
        return []
