import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import json
from openai import OpenAI
from openai_schemas import auction_schema, ebay_sold_items_schema, ebay_search_string_schema
import hashlib
import diskcache as dc
import os

def gen_message_record(role, content):
    return {
        "role": role,
        "content": str(content)
    }

def gen_user_message_record(content):
    return gen_message_record("user", content)

def is_message_record(thing):
    return isinstance(thing, dict) and "role" in thing and "content" in thing and isinstance(thing["content"], str)

def fetch_openai_json(json_schema, messages_arg):
    
    if isinstance(messages_arg, str):
        messages = [gen_user_message_record(messages_arg)]
    
    elif is_message_record(messages_arg):
        messages = [messages_arg]
    
    elif isinstance(messages_arg, list):
        if not all(isinstance(msg, str) or is_message_record(msg) for msg in messages_arg):
            raise ValueError("All items in the messages_arg list must be a string or a message record.")
        messages = [gen_user_message_record(msg) if isinstance(msg, str) else msg for msg in messages_arg]
    
    else:
        raise ValueError("Invalid messages format. Must be a string, a message record, or a list of these.")
    
    response_content = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=16384,
        messages=[
            gen_message_record("system", "You are a helpful data parsing assistant. Please respond in JSON format according to provided schema."),
            gen_message_record("user", json.dumps(json_schema)),
            *messages,
            gen_message_record("user", "Please use the provided data to generate a JSON object that matches the schema")
        ],
        response_format = { "type": "json_object" }
    )
    
    ret = response_content.choices[0].message.content
    # print("type of ret:", type(ret))
    try:
        return json.loads(ret)
    except Exception as e:
        print(f"Error parsing openai json response: {ret}, Error: {e}")
        return None

cache = dc.Cache(os.path.join(os.path.dirname(__file__), 'ebay_demand_cache'))

def opanai_returns_formatted_ebay_demand_data(ebay_sold_items_el, target_item, search_url):
    ret = None

    # Check if the result is already in the cache
    if search_url in cache:
        return cache[search_url]

    response_content = fetch_openai_json(
        ebay_sold_items_schema, 
        [ebay_sold_items_el, 
         str( "\n\nHere is the target item data. We're searching for items similar to this one: ", str(target_item)),
         str("\n\nHere is the search url the ebay html data was fetched from: ", search_url),
         str("\n\nPlease return json response with 'ebay_sold_items' key where value is an array of 'ebay sold item' records according to schema. ",
         "Some of the items in the html do not match the target item we're searching for and should be ignored. ",
         "Others match slightly and should be included with a lower likeness score. ")])
    
    if response_content and "ebay_sold_items" in response_content:
        ret = response_content["ebay_sold_items"]
    elif response_content and "data" in response_content:
        ret = response_content["data"]
    else:
        print(f"Unexpected response structure: {response_content}")
        raise Exception(f"Unexpected response structure: {response_content}")

    # Store the result in the cache
    cache[search_url] = ret

    return ret

import hashlib

ebay_search_string_cache = dc.Cache(os.path.join(os.path.dirname(__file__), 'ebay_search_string_cache'))

def openai_returns_ebay_search_string(auction_data, item_data):

    inputs_hash = hashlib.sha256(str(item_data).encode()).hexdigest()

    if inputs_hash in ebay_search_string_cache:
        return ebay_search_string_cache[inputs_hash]

    message1 = gen_user_message_record("Here is the auction data for context: " + str(auction_data))
    message2 = gen_user_message_record("Here is the item data to create a search string for: " + str(item_data))
    messages = [message1, message2]
    response_content = fetch_openai_json(ebay_search_string_schema, messages)

    if "ok" not in response_content or "search_string" not in response_content:
        raise ValueError("openai_returns_ebay_search_string response content must contain both 'ok' and 'search_string' keys.")

    ok = response_content["ok"]
    search_string = response_content["search_string"]

    if ok == "false":
        ebay_search_string_cache[inputs_hash] = ""
        return ""

    ebay_search_string_cache[inputs_hash] = search_string

    return search_string

def openai_returns_formatted_auction_data(auction_data_el, description_el, shipping_el):
    message1 = gen_user_message_record(auction_data_el)
    message2 = gen_user_message_record(description_el)
    message3 = gen_user_message_record(shipping_el)
    messages = [message1, message2, message3]
    response_content = fetch_openai_json(auction_schema, messages)
    # print("response_content:", response_content)
    return response_content

# def test_fetch_openai_json_response():
#     example_schema = json.dumps({
#         "type": "object",
#         "properties": {
#             "a": {
#                 "type": "string"
#             },
#             "b": {
#                 "type": "integer"
#             }
#         },
#         "required": ["a", "b"]
#     })
    
#     message = f"Generate a JSON object that matches the schema"
    
#     response_content = fetch_openai_json(example_schema, message)
#     print("response_content:", response_content)

# test_fetch_openai_json_response()