# Web Scraper for Liquidation Deals

This project is a web scraper designed to gather data from liquidation websites, process it, and provide insights into auction items and their demand. The current implementation focuses on `liquidation.com`.

## Prerequisites

- Python 3.x
- Selenium
- BeautifulSoup
- pandas
- sqlite3

## Setup Instructions

1. **Clone the repository:**

   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install the required Python packages:**
   ```sh
   pip install -r requirements.txt
   ```

## Running the Codebase

### Step-by-Step Process for `liquidation.com`

1. **Initialize the database:**

   ```sh
   cd sitemaps
   python db-init.py
   ```

2. **Run the simple crawler to gather URLs:**

   ```sh
   python simple_crawler.py
   ```

3. **Return to the root directory:**

   ```sh
   cd ..
   ```

4. **Populate the `/csvs` directory with auction item data:**

   ```sh
   python get_liquidation_csvs.py
   ```

5. **Ingest the CSV data and output the `standardized_data.csv` file:**

   ```sh
   python stan_dat_ingest.py
   ```

6. **Generate search terms from the listings:**

   ```sh
   python stan_dat_get_search.py
   ```

7. **(Optional) Get information on the standardized data:**

   ```sh
   python stan_dat_info.py
   ```

8. **Get data on auctions and save to `auction_data.csv`:**
   ```sh
   python get_auction_csvs.py
   ```

## Future Enhancements

1. **Associate auction data in `auction_data.csv` with auction item data in `standardized_data.csv`.**

2. **Search eBay for each item to get eBay selling demand data and output another CSV.**

3. **Rename `standardized_data.csv` to a more appropriate name.**

4. **Use SQLite instead of CSV files for data persistence. Create a standardized database with multiple tables.**

5. **Implement selling demand logic for processing eBay selling data.**

6. **Create an interactive web UI for working with all this data intuitively with filters and search capabilities.**

7. **Work on efficiency optimizations across the board once the first draft of the process is completed.**

## License

This project is licensed under the MIT License.
