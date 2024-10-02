sitemap_table_schema = '''
CREATE TABLE IF NOT EXISTS sitemap_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    parent_id INTEGER,
    depth INTEGER,
    FOREIGN KEY (parent_id) REFERENCES sitemap_data (id) ON DELETE CASCADE
);
'''

auction_data_table_schema = '''
CREATE TABLE IF NOT EXISTS auction_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    auction_id TEXT UNIQUE,
    title TEXT,
    description TEXT,
    closes_datetime TEXT,
    stated_msrp REAL,
    buy_now_price REAL,
    views INTEGER,
    bids INTEGER,
    bidders INTEGER,
    watching INTEGER,
    location TEXT,
    seller TEXT,
    condition TEXT,
    shipping_terms TEXT,
    shipping_estimate TEXT,
    total_weight REAL,
    quantity_in_lot INTEGER,
    buyers_premium REAL,
    auction_type TEXT,
    minimum_shipping_fee REAL,
    FOREIGN KEY (url) REFERENCES sitemap_data(url)
);
'''

items_data_table_schema = '''
CREATE TABLE IF NOT EXISTS items_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id TEXT,
    data TEXT UNIQUE NOT NULL,
    FOREIGN KEY (auction_id) REFERENCES auction_data(auction_id)
)
'''

ebay_demand_data_table_schema = '''
    CREATE TABLE IF NOT EXISTS ebay_demand_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auction_id TEXT,
        item_id INTEGER,
        search_string TEXT,
        url TEXT,
        ebay_item_name TEXT,
        ebay_item_price TEXT,
        ebay_item_condition TEXT,
        ebay_item_sold_date TEXT,
        FOREIGN KEY (auction_id) REFERENCES auction_data(auction_id),
        FOREIGN KEY (item_id) REFERENCES items_data(id)
    )
'''

sql_drop_tables = '''
DROP TABLE IF EXISTS sitemap_data;
DROP TABLE IF EXISTS auction_data;
DROP TABLE IF EXISTS items_data;
DROP TABLE IF EXISTS ebay_demand_data;
'''
