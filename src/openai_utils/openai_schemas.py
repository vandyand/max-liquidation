ebay_sold_items_schema = {
    "type": "object",
    "properties": {
        "ebay_sold_items": {
            "type": "array",
            "description": "Array of eBay sold items",
            "items": {
                "type": "object",
                "description": "Single eBay sold item",
                "properties": {
                    "ebay_item_name": {
                        "type": "string",
                        "description": "Name of the item on eBay"
                    },
                    "ebay_item_price": {
                        "type": "number",
                        "description": "Two-decimal-place price of the item on eBay. Of form 123.45 representing USD amount. If price is integer, return it as 123.00"
                    },
                    "ebay_item_condition": {
                        "type": "string",
                        "description": "Condition of the item on eBay (brand new, used, open box, etc.)"
                    },
                    "ebay_item_sold_date": {
                        "type": "string",
                        "description": "Date when the item was sold on eBay"
                    },
                    "ebay_item_likeness_score": {
                        "type": "integer",
                        "description": "Integer score between 0 and 100 that represents how similar the ebay item is to the auction item. 0 means not similar at all, 100 means exact match."
                    }
                },
                "required": [
                    "ebay_item_name",
                    "ebay_item_price",
                    "ebay_item_condition",
                    "ebay_item_sold_date",
                    "ebay_item_likeness_score"
                ]
            }
        }
    },
    "required": ["ebay_sold_items"]
}

ebay_search_string_schema = {
    "type": "object",
    "properties": {
        "ok": {
            "type": "boolean",
            "description": "Whether the search string is valid. If item data is not enough to create a search string, return false"
        },
        "search_string": {
            "type": "string",
            "description": "Search string to use for finding recently sold eBay items. Return empty string if search string is not valid. Try to optimize the search string for finding highly similar items. In general, shorter search strings are better."
        }
    },
    "required": ["ok", "search_string"]
}

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
        "closes_datetime": {
            "type": "string",
            "description": "Datetime when the auction closes"
        },
        "stated_msrp": {
            "type": "real",
            "description": "Stated MSRP of the auction. Of form 123.45 representing USD amount"
        },
        "buy_now_price": {
            "type": "real",
            "description": "Buy now price of the auction. Of form 123.45 representing USD amount"
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
    "required": ["auction_id", "title", "description", "closes_datetime", "buy_now_price", "views", "bids", "bidders", "watching", "location", "seller", "condition", "shipping_terms", "shipping_estimate", "total_weight", "quantity_in_lot", "buyers_premium", "auction_type", "minimum_shipping_fee"]
}