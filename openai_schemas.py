auction_schema = {
    "type": "object",
    "properties": {
        "auction_id": {
            "type": "string",
            "description": "Unique identifier for the auction"
        },
        "title": {
            "type": "string",
            "description": "Title of the auction"
        },
        "description": {
            "type": "string",
            "description": "Description of the auction"
        },
        "time_left": {
            "type": "string",
            "description": "Time left for the auction to end"
        },
        "buy_now_price": {
            "type": "string",
            "description": "Buy now price of the auction"
        },
        "views": {
            "type": "integer",
            "description": "Number of views the auction has received"
        },
        "bids": {
            "type": "integer",
            "description": "Number of bids placed on the auction"
        },
        "bidders": {
            "type": "integer",
            "description": "Number of bidders participating in the auction"
        },
        "watching": {
            "type": "integer",
            "description": "Number of users watching the auction"
        },
        "location": {
            "type": "string",
            "description": "Location of the auction item"
        },
        "seller": {
            "type": "string",
            "description": "Seller of the auction item"
        },
        "condition": {
            "type": "string",
            "description": "Condition of the auction item"
        },
        "shipping_terms": {
            "type": "string",
            "description": "Shipping terms for the auction item"
        },
        "shipping_estimate": {
            "type": "string",
            "description": "Estimated shipping cost for the auction item"
        },
        "total_weight": {
            "type": "string",
            "description": "Total weight of the auction item"
        },
        "quantity_in_lot": {
            "type": "string",
            "description": "Quantity of items in the auction lot"
        },
        "buyers_premium": {
            "type": "string",
            "description": "Buyer's premium for the auction"
        },
        "auction_type": {
            "type": "string",
            "description": "Type of the auction"
        },
        "minimum_shipping_fee":{
            "type": "string",
            "description": "Minimum shipping fee for the auction item"
        }
    },
    "required": ["auction_id", "title", "description", "time_left", "buy_now_price", "views", "bids", "bidders", "watching", "location", "seller", "condition", "shipping_terms", "shipping_estimate", "total_weight", "quantity_in_lot", "buyers_premium", "auction_type", "minimum_shipping_fee"]
}