import json
from openai import OpenAI
from openai_schemas import auction_schema

def gen_message_record(role, content):
    return {
        "role": role,
        "content": content
    }

def fetch_openai_json(json_schema, messages):
    response_content = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[
            gen_message_record("system", "You are a helpful assistant. Please respond in JSON format according to provided schema."),
            gen_message_record("user", json.dumps(json_schema)),
            *messages
        ],
        response_format = { "type": "json_object" }
    )
    ret = response_content.choices[0].message.content
    return json.loads(ret)

def openai_returns_formatted_auction_data(auction_data_el, description_el, shipping_el):
    message1 = gen_message_record("user", auction_data_el)
    message2 = gen_message_record("user", description_el)
    message3 = gen_message_record("user", shipping_el)
    message4 = gen_message_record("user", "Please use the provided data to generate a JSON object that matches the schema")
    messages = [message1, message2, message3, message4]
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