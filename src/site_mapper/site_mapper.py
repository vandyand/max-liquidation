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
import heapq
import diskcache as dc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_utils import create_crud_functions, create_db_connection

class URLNode:
    def __init__(self, url):
        self.url = url
        self.children = []
        self.id = None

    def add_child(self, child_node):
        self.children.append(child_node)

    def __lt__(self, other):
        # This method is required for heapq to compare URLNode instances
        return self.url < other.url

class SimpleCrawler:
    def __init__(self, start_url, max_depth=7):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()  # To keep track of visited URLs
        self.root = URLNode(start_url)
        self.conn = create_db_connection()  # Open connection once

        # Create CRUD functions for the sitemap_data table
        self.sitemap_crud = create_crud_functions('sitemap_data')

        # Set up Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)  # Use the path from `which chromedriver`

        # Initialize diskcache
        self.cache = dc.Cache(os.path.join(os.path.dirname(__file__), 'url_cache'))

    def insert_url_and_get_id(self, url, parent_id, depth):
        """Helper method to insert URL into the database and return its ID."""
        data = {'url': url, 'parent_id': parent_id, 'depth': depth}
        return self.sitemap_crud['insert_or_ignore'](data, self.conn)

    def get_link_href(self, link):
        """Helper method to get the href attribute of a link and skip if it causes issues."""
        try:
            return link.get_attribute('href')
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException encountered for link on {self.driver.current_url}. Skipping link.")
            return None

    def scrape_and_cache(self, url):
        """Scrape the URLs from the given page and cache the result."""
        if url in self.cache:
            return self.cache[url]

        self.driver.get(url)
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )

        links = list(set(self.driver.find_elements(By.TAG_NAME, 'a')))
        child_urls = []

        for link in links:
            child_url = self.get_link_href(link)
            if not child_url:
                continue  # Skip problematic links

            # Skip invalid URLs and image files
            if child_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')):
                continue

            child_urls.append(child_url)

        self.cache[url] = child_urls
        return child_urls

    def crawl(self):
        # Initialize the priority queue with the root node and depth 0
        queue = []
        heapq.heappush(queue, (0, self.root, 0))  # (priority, node, depth)

        while queue:
            priority, node, depth = heapq.heappop(queue)

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
                child_urls = self.scrape_and_cache(node.url)
                signal.alarm(0)  # Cancel the alarm if the page loads successfully
            except TimeoutError:
                print(f"Timeout while loading {node.url}. Closing page and moving to next URL.")
                self.driver.execute_script("window.stop();")  # Force stop the page load
                signal.alarm(0)  # Cancel the alarm
                continue
            except Exception as e:
                print(f"Error waiting for links on {node.url}: {e}")
                signal.alarm(0)  # Cancel the alarm in case of other exceptions
                continue

            print(f"Found {len(child_urls)} links on {node.url}")

            for child_url in child_urls:
                if "auction/view?id=" in child_url and child_url not in self.visited:
                    child_node = URLNode(child_url)
                    node.add_child(child_node)

                    # Insert child URL with current node ID as parent_id
                    child_node.id = self.insert_url_and_get_id(child_node.url, node.id, depth + 1)

                    # Determine priority: higher priority for URLs containing 'auction', lower for '#'
                    if 'auction/view?' in child_url and '#' not in child_url:
                        priority = 0
                    elif 'auction/search?' in child_url and '#' not in child_url:
                        priority = 1
                    elif '#' in child_url:
                        priority = 3
                    else:
                        priority = 2

                    # Add the child node to the priority queue with incremented depth
                    heapq.heappush(queue, (priority, child_node, depth + 1))

    def close_driver(self):
        self.driver.quit()  # Close the Selenium WebDriver

    def close_db_connection(self):
        if self.conn:
            self.conn.close()

    def close_cache(self):
        self.cache.close()  # Close the diskcache

if __name__ == '__main__':
    start_url = 'https://www.liquidation.com/auction/search?flag=new&searchparam_category1=&searchparam_dimension=10104&searchparam_words=Vacuum'
    # start_url = 'https://www.liquidation.com/'
    # start_url = 'https://www.directliquidation.com/'
    crawler = SimpleCrawler(start_url, max_depth=0)
    try:
        crawler.crawl()  # Start crawling
    except KeyboardInterrupt:
        print("Crawling interrupted by user.")
    finally:
        crawler.close_driver()  # Close the Selenium driver
        crawler.close_db_connection()  # Close the connection when done
        crawler.close_cache()  # Close the cache when done
