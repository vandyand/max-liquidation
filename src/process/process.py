import os
import sys
import json
import time
import urllib.parse
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from diskcache import Cache

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_utils import create_crud_functions, create_db_connection
from openai_utils.openai_base import openai_returns_formatted_auction_data, opanai_returns_formatted_ebay_demand_data
from auction_data.get_auction_data import fetch_auction_data
from items_data.get_auction_items_csvs import fetch_auction_items
from ebay_demand.get_ebay_demand import fetch_ebay_demand

# Initialize FastAPI app
app = FastAPI()

# Pydantic model for request
class AuctionRequest(BaseModel):
    auction_url: str

# Main process function
def process_auction(auction_id):
    conn = create_db_connection()
    auction_url = f"https://www.liquidation.com/auction/view?id={auction_id}"
    try:
        auction_data = fetch_auction_data(auction_url)
        if auction_data is None:
            raise ValueError("Auction data not found")
        
        items_data = fetch_auction_items(auction_id)
        print(f"Items data: {items_data}")
        if items_data is None:
            raise ValueError("Items data not found")
        
        ebay_demand_data = fetch_ebay_demand(items_data)
        
        # # Persist data to the database
        # auction_crud = create_crud_functions('auction_data')
        # items_crud = create_crud_functions('items_data')
        # ebay_demand_crud = create_crud_functions('ebay_demand_data')
        
        # auction_crud['insert_or_ignore'](auction_data, conn)
        # for item in items_data:
        #     items_crud['insert_or_ignore'](item, conn)
        #     for ebay_item in ebay_demand_data:
        #         ebay_item['item_id'] = item[0]
        #         ebay_item['auction_id'] = item[1]
        #         ebay_item['url'] = search_url
        #         ebay_item['search_string'] = search_string
        #         ebay_demand_crud['insert_or_ignore'](ebay_item, conn)
        
        return {
            "auction_data": auction_data,
            "items_data": items_data,
            "ebay_demand_data": ebay_demand_data
        }
    finally:
        if conn:
            conn.close()

# FastAPI endpoint
@app.post("/process_auction")
def process_auction_endpoint(request: AuctionRequest):
    try:
        auction_url = request.auction_url
        auction_id = auction_url.split('=')[1]
        result = process_auction(auction_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
