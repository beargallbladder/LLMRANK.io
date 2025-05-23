from fastapi import FastAPI
from typing import List

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LLMRANK API is live!"}

@app.get("/domains")
def get_domains() -> List[str]:
    return ["microsoft.com", "google.com", "amazon.com"]
