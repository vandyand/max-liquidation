import os
import sys
import json
import time
import urllib.parse
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic model for request
class AuctionRequest(BaseModel):
    auction_url: str

# Function to replace NaN values
def replace_nan_with_none(data):
    if isinstance(data, list):
        return [replace_nan_with_none(item) for item in data]
    elif isinstance(data, dict):
        return {key: replace_nan_with_none(value) for key, value in data.items()}
    elif pd.isna(data):
        return None
    else:
        return data

import hashlib

def consolidate_items_data(items_data):
    hashed_items_data = {}
    for item in items_data:
        sans_qty_id = {key: value for key, value in item.items() if key.lower() not in ["qty", "quantity", "id"]}
        item_hash = hashlib.sha256(str(sans_qty_id).encode()).hexdigest()
        
        # Combine items with the same hash
        if item_hash in hashed_items_data:
            hashed_items_data[item_hash]['Qty'] += item.get('Qty', 0)  # Update quantity
        else:
            # item['hash'] = item_hash
            hashed_items_data[item_hash] = item  # Add new item with hash

    consolidated_items_data = list(hashed_items_data.values()) 
    return consolidated_items_data


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
                
        consolidated_items_data = consolidate_items_data(items_data)

        # Replace NaN values with None
        auction_data = replace_nan_with_none(auction_data)
        consolidated_items_data = replace_nan_with_none(consolidated_items_data)
        
        return {
            "auction_data": auction_data,
            "items_data": consolidated_items_data
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

class EbayDemandRequest(BaseModel):
    items_data: list
    auction_data: dict

class EbayDemandItem(BaseModel):
    ebay_item_name: str
    ebay_item_price: str
    ebay_item_condition: str
    ebay_item_sold_date: str
    ebay_item_sold_days_ago: int
    ebay_item_likeness_score: int
    id: str
    item_id: str
    auction_id: str
    url: str
    search_string: str


class EbayDemandResponse(BaseModel):
    ebay_demand_data: list[EbayDemandItem]
    ebay_demand_score: float

def item_score(ebay_demand_item):
    score = (90 - ebay_demand_item['ebay_item_sold_days_ago']) * ebay_demand_item['ebay_item_likeness_score']
    return max(score, 0)

def calculate_ebay_demand_items_score(ebay_demand_data):
    ebay_demand_item_scores = [item_score(ebay_demand_item) for ebay_demand_item in ebay_demand_data]

    if len(ebay_demand_item_scores) == 0:
        return 0
    
    return (sum(ebay_demand_item_scores) + len(ebay_demand_item_scores)) / len(ebay_demand_item_scores)

def process_ebay_demand(auction_data, items_data):
    ebay_demand_data = fetch_ebay_demand(auction_data, items_data)
    ebay_demand_data = replace_nan_with_none(ebay_demand_data)
    ebay_demand_score = calculate_ebay_demand_items_score(ebay_demand_data)
    return ebay_demand_data, ebay_demand_score

@app.post("/process_ebay_demand", response_model=EbayDemandResponse)
def process_ebay_demand_endpoint(request: EbayDemandRequest):
    try:
        items_data = request.items_data
        auction_data = request.auction_data
        ebay_demand_data, ebay_demand_score = process_ebay_demand(auction_data, items_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing eBay demand: {str(e)}")

    return EbayDemandResponse(ebay_demand_data=ebay_demand_data, ebay_demand_score=ebay_demand_score)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)