import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
from db.db_utils import create_crud_functions, create_db_connection

download_dir = os.path.join(os.path.dirname(__file__), 'csvs')

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set download directory
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    print(f"Download directory set to: {download_dir}")
    
    return driver

def wait_for_downloads(timeout=30):
    seconds = 0
    dl_wait = True
    
    while dl_wait and seconds < timeout:
        dl_wait = False
        
        for fname in os.listdir(download_dir):
            if fname.endswith('.crdownload'):
                dl_wait = True
        
        seconds += 1
        time.sleep(0.25)
    
    return not dl_wait

def download_file(driver, url):
    auction_id = url.split('=')[1]

    file_path = os.path.join(download_dir, f'm{auction_id}.csv')
    
    if os.path.exists(file_path):
        print(f"File {file_path} already exists. Skipping download.")
        return
    
    try:
        driver.get(url)
        
        # Wait for the download to complete
        if wait_for_downloads():
            print(f"Downloaded {url}")
        else:
            print(f"Download timed out for {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Ensure the 'csvs' directory exists
os.makedirs(download_dir, exist_ok=True)

# Download each csv_manifest file
def main():
    driver = setup_driver()
    
    try:
        conn = create_db_connection()
        auction_crud = create_crud_functions('auction_data')
        
        records = auction_crud['get_all'](conn)
        
        if records:
            for record in records:
                auction_id = record[2]
                url = f'https://www.liquidation.com/auction/csv_manifest?auctionId={auction_id}'
                download_file(driver, url)
                time.sleep(0.1)
                
        else:
            print("No auction records found.")
    except KeyboardInterrupt:
        print("Download interrupted by user.")
    finally:
        driver.quit()
        
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
