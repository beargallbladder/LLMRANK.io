from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from secrets import OPENAI_API_KEY, GEMINI_API_KEY, DEEP_SEEK_API_KEY
import openai
import requests

app = FastAPI()

# Set keys
openai.api_key = OPENAI_API_KEY

# Request schema
class PromptRequest(BaseModel):
    provider: Literal["openai", "gemini", "deepseek"]
    prompt: str

@app.get("/")
def root():
    return {"message": "LLMRANK API is live with multi-LLM access."}

@app.post("/generate")
def generate_text(req: PromptRequest):
    provider = req.provider
    prompt = req.prompt.strip()

    if provider == "openai":
        return generate_openai(prompt)
    elif provider == "gemini":
        return generate_gemini(prompt)
    elif provider == "deepseek":
        return generate_deepseek(prompt)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider.")

# -----------------------------------------
# OpenAI (GPT-4 or GPT-3.5)
def generate_openai(prompt: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return {"model": "openai", "response": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------
# Google Gemini
def generate_gemini(prompt: str):
    try:
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        resp = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return {"model": "gemini", "response": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------
# DeepSeek
def generate_deepseek(prompt: str):
    try:
        headers = {
            "Authorization": f"Bearer {DEEP_SEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        message = resp.json()["choices"][0]["message"]["content"]
        return {"model": "deepseek", "response": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
