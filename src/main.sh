#!/bin/bash

# delete stuff
python src/delete_caches.py
python src/items_data/delete_csvs.py

# reinitialize db
python src/db/db_init.py
python src/db/db_test.py

# write sitemap to db
python src/site_mapper/site_mapper.py

# get and write auction data to db
python src/auction_data/get_auction_data.py

# get and write auction items to db
python src/items_data/get_auction_items_csvs.py
python src/items_data/items_data_ingest.py
python src/items_data/main.py

# get and write ebay demand data to db
python src/ebay_demand/get_ebay_demand.py
