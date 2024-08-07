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
    auction_id TEXT UNIQUE,
    title TEXT,
    description TEXT,
    time_left TEXT,
    buy_now_price TEXT,
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
    minimum_shipping_fee REAL
);
'''
items_data_table_schema = '''
CREATE TABLE IF NOT EXISTS items_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id TEXT,
    item_id INTEGER,
    product_code TEXT,
    product_name TEXT,
    additional_info TEXT,
    price REAL,
    currency TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    model TEXT,
    description TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    sku TEXT,
    upc TEXT,
    ean TEXT,
    isbn TEXT,
    jan TEXT,
    mpn TEXT,
    gtin TEXT,
    asin TEXT,
    item_url TEXT,
    image_url TEXT,
    weight REAL,
    dimensions TEXT,
    color TEXT,
    size TEXT,
    material TEXT,
    condition TEXT,
    availability TEXT,
    shipping_cost REAL,
    shipping_time TEXT,
    seller_id TEXT,
    seller_name TEXT,
    seller_rating REAL,
    seller_feedback_count INTEGER,
    seller_location TEXT,
    seller_contact TEXT,
    return_policy TEXT,
    warranty TEXT,
    date_added TEXT,
    last_updated TEXT,
    FOREIGN KEY (auction_id) REFERENCES auction_data(auction_id)
);
'''

ebay_demand_data_table_schema = '''
    CREATE TABLE IF NOT EXISTS ebay_demand_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        auction_id TEXT,
        item_id INTEGER,
        search_string TEXT,
        ebay_item_name TEXT,
        ebay_item_price TEXT,
        ebay_item_condition TEXT,
        ebay_item_url TEXT,
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
