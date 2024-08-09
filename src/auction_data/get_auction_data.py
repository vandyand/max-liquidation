import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from openai_utils.openai_base import openai_returns_formatted_auction_data
from diskcache import Cache

# Import database utility functions
from db.db_utils import create_crud_functions, create_connection

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    return driver

driver = setup_driver()

def get_relevant_auction_elements(auction_url):
    driver.get(auction_url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bodyContainer"))
        )
    except Exception as e:
        print(f"Timeout waiting for auction page to load for auction url {auction_url}: {e}")
        return None
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    try:
        auction_data_element = soup.find(id="auctionData").get_text()
        description_table = soup.find(id="description_table").get_text()
        shipping_table = soup.find(id="shipping_table").get_text()
    except AttributeError as e:
        print(f"Error processing auction url {auction_url}: {e}")
        return None
    
    return (auction_data_element, description_table, shipping_table)

cache = Cache(os.path.join(os.path.dirname(__file__), 'auction_cache'))

def fetch_auction_data(auction_url):

    if auction_url in cache:
        print(f"Cache hit for auction url {auction_url}")
        return cache[auction_url]

    auction_data_element, description_table, shipping_table = get_relevant_auction_elements(auction_url)

    print(f"Formatting data for auction url {auction_url}")
    auction_data = openai_returns_formatted_auction_data(auction_data_element, description_table, shipping_table)

    auction_data['url'] = auction_url

    cache[auction_url] = auction_data

    return auction_data

if __name__ == '__main__':
    try:
        # Create a connection to the database
        conn = create_connection()
        
        # Create CRUD functions for the sitemap_data and auction_data tables
        sitemap_crud = create_crud_functions('sitemap_data')
        auction_crud = create_crud_functions('auction_data')
        
        # Fetch auction IDs from the sitemap_data table
        sitemap_data = sitemap_crud['get_all'](conn)
        urls = [row[1] for row in sitemap_data]
        auction_urls = [url for url in urls if 'auction/view?id=' in url]
        
        driver = setup_driver()

        try:
            for auction_url in auction_urls:
                # Check if auction_url is already in the auction_data table
                existing_auction = auction_crud['get_by_column']('url', auction_url, conn)
                
                if existing_auction:
                    print(f"Skipping auction url {auction_url} as it is already in the database")
                    continue
                
                print(f"Fetching data for auction url {auction_url}")
                auction_data = fetch_auction_data(auction_url)
                
                if auction_data:
                    auction_crud['insert'](auction_data, conn)
        finally:
            driver.quit()
            conn.close()

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        conn.close()
