from sitemaps.db import create_connection, get_all
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    download_dir = os.path.abspath('csvs')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set download directory
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    driver = webdriver.Chrome(service=Service('/opt/homebrew/bin/chromedriver'), options=chrome_options)
    print(f"Download directory set to: {download_dir}")
    return driver

def wait_for_downloads(download_dir, timeout=30):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        print(f"Waiting for downloads to complete: {seconds} seconds")
        dl_wait = False
        for fname in os.listdir(download_dir):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
        time.sleep(0.25)
    return not dl_wait

def download_file(driver, url, download_dir):
    print(f"Downloading {url}")
    try:
        driver.get(url)
        
        # Wait for the download to complete
        if wait_for_downloads(download_dir):
            print(f"Downloaded {url}")
            # Check if the file exists in the download directory
            downloaded_files = os.listdir(download_dir)
            print(f"Files in download directory: {downloaded_files}")
        else:
            print(f"Download timed out for {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Ensure the 'csvs' directory exists
os.makedirs('csvs', exist_ok=True)

# Download each csv_manifest file
if __name__ == '__main__':
    driver = setup_driver()
    try:
        conn = create_connection('sitemaps/big_liq_urls.db')
        records = get_all(conn)
        filtered_records = [record for record in records if 'csv_manifest' in record[1]]
        
        if filtered_records:
            for record in filtered_records:
                url = record[1]
                download_file(driver, url, 'csvs')
        else:
            print("No csv_manifest URLs found.")
    except KeyboardInterrupt:
        print("Download interrupted by user.")
    finally:
        driver.quit()
        if conn:
            conn.close()