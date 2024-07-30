import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scraper.direct_liquidation_scraper import scrape_direct_liquidation
from models import Listing, Item

class TestDirectLiquidationScraper(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def tearDown(self):
        self.driver.quit()

    def test_scrape_direct_liquidation(self):
        listings = scrape_direct_liquidation(self.driver)
        # Check that we got some listings
        self.assertGreater(len(listings), 0, "Should have found at least one listing")
        # Check that each listing has a title and a URL
        for listing in listings:
            self.assertIsInstance(listing, Listing)
            self.assertIsNotNone(listing.title)
            self.assertIsNotNone(listing.url)
            # Check if the items in the listing are valid
            for item in listing.items:
                self.assertIsInstance(item, Item)
                self.assertIsNotNone(item.name)
                self.assertIsNotNone(item.price)
                self.assertIsNotNone(item.url)

if __name__ == '__main__':
    unittest.main()
