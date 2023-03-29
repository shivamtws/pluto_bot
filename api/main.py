from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tiktoken
import json
from starlette.exceptions import HTTPException
from config import settings

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
    if os.environ.get('OPENAI_API_KEY') == None:
        os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY 
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


    # Check Tokens
    tokens = num_tokens_from_messages(messages)
    while tokens >= 4000:
        if messages.count == 1:
            raise HTTPException(status_code=413, detail="Large Size Content.")
        else:
            # Need to Maintained the New Version of Message List
            del messages[1]
            tokens = num_tokens_from_messages(messages)

    
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    query = json.dumps(messages, separators=(',', ':'))
    response = index.query(query, response_mode="compact")

    # Replace KIP: if includes in response
    kip_reply = response.response.replace("KIP:", "")


    return {
        'response': kip_reply
    }
