import requests
from db import insert_url, fetch_tree, create_connection
from urllib.parse import urljoin
from bs4 import BeautifulSoup
# import time
# import random

class URLNode:
    def __init__(self, url):
        self.url = url
        self.children = []
        self.id = None  # To store the ID after inserting into the DB

    def add_child(self, child_node):
        self.children.append(child_node)

class SimpleCrawler:
    def __init__(self, start_url, max_depth=7):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()  # To keep track of visited URLs
        self.root = URLNode(start_url)
        self.conn = create_connection('urls.db')  # Open connection once

    def insert_url_and_get_id(self, url, parent_id, depth):
        """Helper method to insert URL into the database and return its ID."""
        return insert_url(url, parent_id, depth, self.conn)

    def crawl(self, node, depth):
        if depth > self.max_depth:
            return
        
        # Persist the current URL in the DB
        if node.url not in self.visited:
            node.id = self.insert_url_and_get_id(node.url, None, depth)
            self.visited.add(node.url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(node.url, headers=headers, timeout=5)  # Set a timeout
            response.raise_for_status()  # Raise an error for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {node.url}: {e}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # time.sleep(random.uniform(0.5, 1.5))  # Delay for some seconds

        # Find all links on the page
        for link in soup.find_all('a', href=True):
            child_url = link['href']
            # Skip invalid URLs and image files
            if child_url.startswith('#') or child_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')):
                continue
            
            # Resolve relative URLs
            full_url = urljoin(node.url, child_url)
            if full_url not in self.visited and full_url.startswith(self.start_url):
                self.visited.add(full_url)
                child_node = URLNode(full_url)
                node.add_child(child_node)
                
                # Insert child URL with current node ID as parent_id
                child_node.id = self.insert_url_and_get_id(child_node.url, node.id, depth + 1)
                
                # Recursive crawl on the new URL
                self.crawl(child_node, depth + 1)

    def start_crawl(self):
        self.visited.add(self.start_url)
        self.crawl(self.root, 0)

    def print_tree(self, node, level=0):
        print('  ' * level + node.url)
        for child in node.children:
            self.print_tree(child, level + 1)

    def close_connection(self):
        if self.conn:
            self.conn.close()

if __name__ == '__main__':
    start_url = 'https://www.directliquidation.com/'
    # start_url = 'https://www.liquidation.com/'
    crawler = SimpleCrawler(start_url)
    crawler.start_crawl()
    crawler.print_tree(crawler.root)
    crawler.close_connection()  # Close the connection when done