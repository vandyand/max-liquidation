from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from collections import deque
import time
import random
import signal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.db_utils import create_crud_functions, create_connection

class URLNode:
    def __init__(self, url):
        self.url = url
        self.children = []
        self.id = None

    def add_child(self, child_node):
        self.children.append(child_node)

class SimpleCrawler:
    def __init__(self, start_url, max_depth=7):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()  # To keep track of visited URLs
        self.root = URLNode(start_url)
        self.conn = create_connection()  # Open connection once

        # Create CRUD functions for the sitemap_data table
        self.sitemap_crud = create_crud_functions('sitemap_data')

        # Set up Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)  # Use the path from `which chromedriver`

    def insert_url_and_get_id(self, url, parent_id, depth):
        """Helper method to insert URL into the database and return its ID."""
        data = {'url': url, 'parent_id': parent_id, 'depth': depth}
        return self.sitemap_crud['insert'](data, self.conn)

    def get_link_href(self, link):
        """Helper method to get the href attribute of a link and skip if it causes issues."""
        try:
            return link.get_attribute('href')
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException encountered for link on {self.driver.current_url}. Skipping link.")
            return None

    def crawl(self):
        queue = deque([(self.root, 0)])  # Initialize the queue with the root node and depth 0

        while queue:
            node, depth = queue.popleft()

            if depth > self.max_depth:
                continue

            if node.url in self.visited:
                continue

            self.visited.add(node.url)
            print(f"Crawling URL: {node.url}")

            def timeout_handler(signum, frame):
                raise TimeoutError("Crawling timed out")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # Set the timeout to 10 seconds

            try:
                self.driver.get(node.url)
                WebDriverWait(self.driver, 2.5).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'a'))
                )
                signal.alarm(0)  # Cancel the alarm if the page loads successfully
            except Exception as e:
                print(f"Error waiting for links on {node.url}: {e}")
                signal.alarm(0)  # Cancel the alarm in case of other exceptions
                continue

            # Find all links on the page and enforce uniqueness
            links = list(set(self.driver.find_elements(By.TAG_NAME, 'a')))

            print(f"Found {len(links)} links on {node.url}")

            for link in links:
                child_url = self.get_link_href(link)
                if not child_url:
                    continue  # Skip problematic links

                # Skip invalid URLs and image files
                if child_url.startswith('#') or child_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '#')):
                    continue

                # Resolve relative URLs
                if child_url.startswith(self.start_url) and child_url not in self.visited:
                    child_node = URLNode(child_url)
                    node.add_child(child_node)

                    # Insert child URL with current node ID as parent_id
                    child_node.id = self.insert_url_and_get_id(child_node.url, node.id, depth + 1)

                    # Add the child node to the queue with incremented depth
                    queue.append((child_node, depth + 1))

    def close_driver(self):
        self.driver.quit()  # Close the Selenium WebDriver

    def close_db_connection(self):
        if self.conn:
            self.conn.close()

if __name__ == '__main__':
    start_url = 'https://www.liquidation.com/'
    # start_url = 'https://www.directliquidation.com/'
    crawler = SimpleCrawler(start_url)
    try:
        crawler.crawl()  # Start crawling
    except KeyboardInterrupt:
        print("Crawling interrupted by user.")
    finally:
        crawler.close_driver()  # Close the Selenium driver
        crawler.close_db_connection()  # Close the connection when done