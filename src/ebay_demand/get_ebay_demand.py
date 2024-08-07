# read data from ../items_data.csv

# for each item in items
#    get search string from item
#    use web driver to go to ebay.com
#    search ebay using the item search string
#    add "&LH_Sold=1&LH_Complete=1" to end of url to get recently completed, sold listings (see example urls below)
#    get ul element with classname: class="srp-results srp-list clearfix"
#    send ul element to chatgpt 4o mini to get a list of all the items in the ul element
#    each sold item should have the following data:
#        item id (randomly generated uuid)
#        item name
#        item price
#        item condition (brand new, used, open box, etc etc)
#        item url
#        item sold date
#        append item data to a csv file using pandas dataframe 


# example unfiltered search url: ```https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1312&_nkw=B0BZTGL6LG+Andis+74150+GTX-EXO+Professional+Cord%2FCordless+Lithium-ion+Electric+Beard+%26+Hair+Trimmer+with+Charging+Stand%2C+Black+%2CB0BZTGL6LG+40102741500%2C&_sacat=0```
# example filtered search url: ```https://www.ebay.com/sch/i.html?_from=R40&_nkw=B0BZTGL6LG+Andis+74150+GTX-EXO+Professional+Cord%2FCordless+Lithium-ion+Electric+Beard+%26+Hair+Trimmer+with+Charging+Stand%2C+Black+%2CB0BZTGL6LG+40102741500%2C&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1```


import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time
import uuid
import sys
sys.path.append('..')
from openai_base import opanai_returns_formatted_ebay_demand_data
from openai_schemas import ebay_demand_schema
import urllib.parse
import sqlite3

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    return driver

def fetch_ebay_demand_data(driver, item_search_string):
    encoded_search_string = urllib.parse.quote(item_search_string)
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_search_string}&LH_Sold=1&LH_Complete=1"
    driver.get(search_url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "srp-results"))
        )
    except Exception as e:
        print(f"Timeout waiting for eBay search results for item {item_search_string}: {e}")
        return None
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    try:
        results_list = soup.find("ul", class_="srp-results srp-list clearfix").get_text()
        # print(f"results_list: {results_list[:100]}")
        return results_list
    except AttributeError as e:
        print(f"Error processing eBay search results for item {item_search_string}: {e}")
        return None

def main():
    # Read item names and auction IDs from items_data.csv
    df = pd.read_csv("../items_data.csv", low_memory=False)
    item_search_strings = df[['auction_id', 'search']].drop_duplicates()
    
    driver = setup_driver()
    
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('ebay_demand_data.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ebay_demand_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auction_id TEXT,
            search_string TEXT,
            item_name TEXT,
            item_price TEXT,
            item_condition TEXT,
            item_url TEXT,
            item_sold_date TEXT
        )
    ''')
    
    try:
        for _, row in item_search_strings.iterrows():
            auction_id = row['auction_id']
            search_string = row['search']
            print(f"Fetching eBay demand data for item {search_string}")
            item_data_list = fetch_ebay_demand_data(driver, search_string)
            
            if item_data_list:
                print(f"Formatting ebay demand data for item {search_string}")
                formatted_data = opanai_returns_formatted_ebay_demand_data(item_data_list)
                
                # Ensure formatted_data is a list of dictionaries
                if isinstance(formatted_data, list) and all(isinstance(item, dict) for item in formatted_data):
                    # Add auction_id and search_string to each item
                    for item in formatted_data:
                        item['auction_id'] = auction_id
                        item['search_string'] = search_string
                    
                    formatted_df = pd.DataFrame(formatted_data)
                    formatted_df.to_sql('ebay_demand_data', conn, if_exists='append', index=False)
                else:
                    print(f"Unexpected formatted data structure: {formatted_data}")
    finally:
        driver.quit()
        conn.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Process interrupted by user.")