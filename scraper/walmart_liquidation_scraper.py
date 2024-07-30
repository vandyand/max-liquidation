from selenium import webdriver
from models import Listing, Item
import time

# Function to scrape Walmart Liquidation Auctions

def scrape_walmart_liquidation(driver):
    driver.get('https://liquidations.walmart.com/')
    time.sleep(3)  # Wait for the page to load
    listings = []
    # Find listing elements on the page
    items = driver.find_elements('css selector', '.auction-listing')

    for item_element in items:
        title = item_element.find_element('css selector', '.listing-title').text
        url = item_element.find_element('css selector', 'a').get_attribute('href')
        listing = Listing(title, url)
        
        # Scrape item details for this listing
        item_name = item_element.find_element('css selector', '.item-description').text
        item_price = item_element.find_element('css selector', '.item-price').text
        item_url = item_element.find_element('css selector', 'a').get_attribute('href')
        item = Item(item_name, item_price, item_url)
        listing.add_item(item)
        listings.append(listing)
    return listings

