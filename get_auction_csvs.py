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
from openai_base import openai_returns_formatted_auction_data

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    return driver

def fetch_auction_data(driver, auction_id):
    url = f"https://www.liquidation.com/auction/view?id={auction_id}"
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bodyContainer"))
        )
    except Exception as e:
        print(f"Timeout waiting for auction page to load for auction ID {auction_id}: {e}")
        return None
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    auction_data_element = soup.find(id="auctionData").get_text()
    description_table = soup.find(id="description_table").get_text()
    shipping_table = soup.find(id="shipping_table").get_text()

    print(f"Formatting data for auction ID {auction_id}")
    auction_data = openai_returns_formatted_auction_data(auction_data_element, description_table, shipping_table)
    
    return auction_data

def main():
    # Read auction IDs from items_data.csv
    df = pd.read_csv("items_data.csv", low_memory=False)
    auction_ids = df['auction_id'].unique()
    
    driver = setup_driver()
    
    # Check if the output file exists
    output_file = "auction_data.csv"
    if os.path.exists(output_file):
        auction_data_df = pd.read_csv(output_file)
    else:
        auction_data_df = pd.DataFrame(columns=[
            "id", "auction_id", "title", "description", "time_left", "buy_now_price", "views", "bids", "bidders", "watching",
            "location", "seller", "condition", "shipping_terms", "shipping_estimate", "total_weight", "quantity_in_lot",
            "buyers_premium", "auction_type", "minimum_shipping_fee"
        ])
    
    try:
        next_id = auction_data_df['id'].max() + 1 if not auction_data_df.empty else 1
        
        for auction_id in auction_ids:
            print(f"Fetching data for auction ID {auction_id}")
            auction_data = fetch_auction_data(driver, auction_id)
            
            if auction_data:
                auction_data['id'] = next_id
                next_id += 1
                auction_data_df = pd.concat([auction_data_df, pd.DataFrame([auction_data])], ignore_index=True)
                auction_data_df.to_csv(output_file, index=False)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()