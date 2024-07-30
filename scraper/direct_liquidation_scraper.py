from selenium import webdriver
from models import Listing, Item
import time

# Function to scrape Direct Liquidation

def scrape_direct_liquidation(driver):
    driver.get('https://www.directliquidation.com/')
    time.sleep(3)  # Wait for the page to load
    listings = []
    print("Waiting for the page to load...")  
    items = driver.find_elements('css selector', 'div.product-item')
    print(f"Found {len(items)} items on the page.")
    
    for item_element in items:
        title = item_element.find_element('css selector', 'h4.product-title').text
        url = item_element.find_element('css selector', 'a').get_attribute('href')
        listing = Listing(title, url)
        
        # Scrape item details for this listing
        item_name = item_element.find_element('css selector', 'h5.item-name').text
        item_price = item_element.find_element('css selector', 'span.product-price').text
        item_url = item_element.find_element('css selector', 'a').get_attribute('href')
        item = Item(item_name, item_price, item_url)
        listing.add_item(item)
        listings.append(listing)
    print(f"Total listings collected: {len(listings)}")
    return listings

