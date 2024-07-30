from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up options for headless browser
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Set up the Chrome WebDriver with headless mode
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Go to Google
driver.get('https://www.google.com/')

# Find the search box
search_box = driver.find_element('name', 'q')

# Search for "best online liquidation container listings"
search_box.send_keys('best online liquidation container listings')
search_box.send_keys(Keys.RETURN)

# Wait for results to load
time.sleep(3)

# Scraping the titles and URLs
results = driver.find_elements('css selector', 'h3')

# Collecting the top results
search_results = []
for result in results:
    parent = result.find_element('xpath', '..')  # Get the parent element to find the link
    search_results.append((result.text, parent.get_attribute('href')))

# Close the browser
driver.quit()

# Output results
for title, url in search_results:
    print(title, url)