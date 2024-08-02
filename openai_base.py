import json
from openai import OpenAI
from openai_schemas import auction_schema, ebay_demand_schema

def gen_message_record(role, content):
    return {
        "role": role,
        "content": content
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
        messages = [gen_user_message_record(msg) if isinstance(msg, str) else msg for msg in messages_arg]
    
    else:
        raise ValueError("Invalid messages format. Must be a string, a message record, or a list of these.")
    
    response_content = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=10000,
        messages=[
            gen_message_record("system", "You are a helpful assistant. Please respond in JSON format according to provided schema."),
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

def opanai_returns_formatted_ebay_demand_data(ebay_sold_items_el):
    response_content = fetch_openai_json(ebay_demand_schema, [ebay_sold_items_el, "Please use 'items' key in json response with value of array of ebay sold item records"])
    
    if response_content and "items" in response_content:
        return response_content["items"]
    elif response_content and "data" in response_content:
        return response_content["data"]
    else:
        print(f"Unexpected response structure: {response_content}")
        return None

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