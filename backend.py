from fastapi import FastAPI, HTTPException
import uuid
from pydantic import BaseModel
from openai import OpenAI

DEEPSEEK_API_KEY = "sk-e4a3846d6f064c17988d59f4900aefa7"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

app = FastAPI()

tokens = {}
MAX_TOKENS = 75

class AskRequest(BaseModel):
    token: str
    question: str

def count_input_tokens(text: str) -> int:
    """Very naive token count (splits by space)."""
    return len(text.split())

@app.get("/generate_link")
def generate_link():
    """Generate a temporary demo link with quota."""
    token = str(uuid.uuid4())
    tokens[token] = {"used": 0, "max": MAX_TOKENS}
    return {"token": token}

@app.post("/ask")
def ask(req: AskRequest):
    token = req.token
    question = req.question

    if token not in tokens:
        tokens[token] = {"used": 0, "max": MAX_TOKENS}

    input_tokens = count_input_tokens(question)
    used_tokens = tokens[token]["used"]
    max_tokens = tokens[token]["max"]

    if used_tokens + input_tokens > max_tokens:
        raise HTTPException(status_code=403, detail="Quota exceeded")

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
        )
        deepseek_answer = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek error: {str(e)}")

    tokens[token]["used"] += input_tokens
    remaining = tokens[token]["max"] - tokens[token]["used"]

    return {
        "answer": deepseek_answer,
        "tokens_remaining": remaining,
        "last_question_tokens": input_tokens,
    }
