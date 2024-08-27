from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auction_data.get_auction_data import fetch_auction_data
from items_data.get_auction_items_csvs import fetch_auction_items
from ebay_demand.get_ebay_demand import fetch_ebay_demand

app = FastAPI()

class AuctionRequest(BaseModel):
    auction_url: str

@app.post("/process_auction")
def process_auction(request: AuctionRequest):
    try:
        print(f"Processing auction for URL: {request.auction_url}")
        process_auction_data(request.auction_url)
        auction_data = fetch_auction_data(request.auction_url)
        if auction_data is None:
            raise HTTPException(status_code=404, detail="Auction data not found")
        
        items_data = fetch_auction_items(request.auction_url)
        ebay_demand_data = fetch_ebay_demand(items_data)
        
        return {
            "auction_data": auction_data,
            "items_data": items_data,
            "ebay_demand_data": ebay_demand_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
