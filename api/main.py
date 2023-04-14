from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tiktoken
import json
from starlette.exceptions import HTTPException
from config import settings

import requests
from bs4 import BeautifulSoup

# import the time module
import time

from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model Definition
class Message(BaseModel):
    content: str
    role: str



# Error Handler
@app.exception_handler(Exception)
def handle_exception(request, exc):
    # Do something with the exception
    return {"message": "Error Here!"}


# Utilities

# Get Open API Key
def get_open_api_key():
    #if os.environ.get('OPENAI_API_KEY') == None:
        #os.environ['OPENAI_API_KEY'] = settings.open_ai 
    # os.environ['OPENAI_API_KEY'] = "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"
    os.environ['OPENAI_API_KEY'] = "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"
    open_key = os.environ.get('OPENAI_API_KEY')
    if open_key == None:
        raise HTTPException(status_code=500, detail="Open Api Key is Missing.")

    return open_key

# Number of Tokens
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
        
def parse_messages(messages):
    txt = ""
    for message in messages:
        if message.get('role') == "User" or message.get('role') == "user":
            txt += "\nQ:"+message.get('content')
        elif message.get('role') == "Assistant" or message.get('role') == "assistant":
            txt += "\nA:"+message.get('content')
        txt += "\n"
    txt += "\n"
    return txt

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/prompt')
async def prompt(data: dict):
    o_key = get_open_api_key()
    
    messages = data.get("data")
    if messages == None:
        raise HTTPException(status_code=422, detail="Missing Message.")
    
    # TODO: Fetch From Redis
    # TODO: ADD Previous Conversation to the Request Message

    # messages.insert(0,  {
    #         "content": "You are a bot whose name is KIP, the Goliath AI Assistant who serves Goliath Technologies. You are here to provide better understanding of products, troubleshooting of products, setting up Goliath products to Goliath users. You have to give instructions, informative steps on how to do things. If the response need steps, show them list of steps. Do not respond outside of Goliath Technology knowledge-base. Do not greet in every response. Every request consider as a question or query. Consider abbreviation in lower case too. Do not introduce yourself.",
    #         "role": "system"
    #     })

    messages.insert(0, {
        "content": "",
        "role": "system"
    })

    # Check Tokens
    tokens = num_tokens_from_messages(messages)
    while tokens >= 4000:
        if messages.count == 1:
            raise HTTPException(status_code=413, detail="Large Size Content.")
        else:
            # Need to Maintained the New Version of Message List
            del messages[1]
            tokens = num_tokens_from_messages(messages)

    messageQuery = parse_messages(messages=messages)
    
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    # query = json.dumps(messages, separators=(',', ':'))

    query = """
        You are a bot whose name is KIP, the Goliath AI Assistant who serves Goliath Technologies. You are here to provide better understanding of products, troubleshooting of products, setting up of products to Goliath users.You have to give instructions, informative steps on how to do things. For configurations, troubleshooting, settin up of products, try to show them list of steps. Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the context, say "I don't know."

    """
    query += messageQuery

    response = index.query(query, response_mode="compact")
    # return response
    # Replace KIP: if includes in response
    kip_reply = response.response.replace("KIP:", "")
    kip_reply = response.response.replace("A:", "")
    kip_reply = kip_reply.replace("\n", "", 1)

    return {
        'response': kip_reply,
        'source_nodes': response.source_nodes
    }


@app.get("/check-user")
def check_insta_user(username: str, platform: str):
    proxies = {
        "proxy": "http://scraperapi:7fd256cb935efe83634cbc7170ae92d1@proxy-server.scraperapi.com:8003",
        "http": "http://scraperapi:7fd256cb935efe83634cbc7170ae92d1@proxy-server.scraperapi.com:8002"
    }

    if platform == 'instagram': 
        
        url = "https://scraper-api.smartproxy.com/v1/scrape"

        payload = {
            "target": "instagram_profile",
            "url": "https://www.instagram.com/"+username
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic UzAwMDAwOTk2NDA6ZEZTMjMxc2EhJEAx"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        json_data=json.loads(response.text)
        response_username=json_data["data"]["content"]["account"]["username"]
	

        if response_username == "":
            # It does not exist in Instagram
            return {'isExist': False}
        else:
            return {'isExist': True}
        
    elif platform == 'facebook':
        url = "https://scrape.smartproxy.com/v1/tasks?universal="

        payload = {
            "target": "universal",
            "url": "https://graph.facebook.com/" + username,
            "headless": "html"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic UzAwMDAwOTk2NDA6ZEZTMjMxc2EhJEAx"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if "does not exist" in response.text:
            return {'isExist': False}
        else:
            return {'isExist': True}
        # if r.text.count('"userID":') >= 1 and r.text.count('"userID":0') <= 0:
        #     return {'isExist': True}
        # else:
        #     # It does not exist in Facebook
        #     return {'isExist': False}
    elif platform == 'tiktok':

        url = "https://scraper-api.smartproxy.com/v1/scrape?tiktok_profile="

        payload = {
            "target": "tiktok_profile",
            "url": "https://www.tiktok.com/@"+username
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic UzAwMDAwOTk2NDA6ZEZTMjMxc2EhJEAx"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code==504:
            return False
        
        
        json_data=json.loads(response.text)
        
        
        response_username=json_data["data"]["content"]["nickname"]
        
        
        if response_username == "":
            
            return {'isExist': False}
            
        else:
        
            return {'isExist': True}
        # r = requests.get('https://www.tiktok.com/@'+username, proxies=proxies, verify=False)
        # if r.text.count("Couldn't find this account") >= 1:
        #     # It does not exist in Tiktok
        #     return {'isExist': False}
        # else:
        #     return {'isExist': True}
        
    return {
        'error': 'Platform or Username not found!'
    }

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
