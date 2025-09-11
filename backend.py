from fastapi import FastAPI,HTTPException
import uuid
import requests
from pydantic import BaseModel

DEEPSEEK_API_KEY="sk-e4a3846d6f064c17988d59f4900aefa7"

app=FastAPI()
tokens={}
MAX_TOKENS=75
class AskRequest(BaseModel):
    token:str
    question:str
def count_input_tokens(text):
    return len(text.split())
@app.get("/generate_link")
def generate_link():
    """Generate a temporary demo link with only quota."""
    token=str(uuid.uuid4())
    tokens[token]={
        "used":0,
        "max":MAX_TOKENS
    }
    return {"token":token}
@app.post("/ask")
def ask(req:AskRequest):
    token=req.token
    if token not in tokens:
        tokens[token]={"used":0,"max":75}
    input_tokens=count_input_tokens(question)
    used_tokens=tokens[token]["used"]
    max_tokens=tokens[token]["max"]
    if used_tokens+input_tokens>max_tokens:
        raise HTTPException(status_code=403,detail="Quota exceeded")
    tokens[token]["used"]+=input_tokens
    response=requests.post("https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization":f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type":"application/json"},
    json={
        "model":"deepseek-chat",
        "messages":[
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":question}
        ],
        "stream":False
    })
    if response.status_code==200:
        data=response.json()
        deepseek_answer=data["choices"][0]["message"]["content"]
        tokens[token]["used"]+=input_tokens
        remaining=tokens[token]["max"]-tokens[token]["used"]
        return {"answer":deepseek_answer,"tokens_remaining":remaining,"last_question_tokens":input_tokens}
    else:
        raise HTTPException(status_code=500,detail=f"Deepseek error:{response.text}")