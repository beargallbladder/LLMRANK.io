"""
LLMRank.io Frontend Server

This module serves a modern, responsive frontend for the LLMRank.io documentation site
and waitlist system for MCP API access.
"""

import os
import json
import datetime
import uuid
import hashlib
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Request, Response, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Make sure directories exist
os.makedirs("data/docs", exist_ok=True)
os.makedirs("data/docs/waitlist", exist_ok=True)
os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)

# Constants
WAITLIST_FILE = "data/docs/waitlist/subscribers.json"
MCP_KEYS_DIR = "data/mcp/keys"
ADMIN_API_KEY = "mcp_81b5be8a0aeb934314741b4c3f4b9436"

# Initialize FastAPI app
app = FastAPI(title="LLMRank.io Frontend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates = Jinja2Templates(directory="frontend/templates")

# Initialize waitlist if it doesn't exist
if not os.path.exists(WAITLIST_FILE):
    with open(WAITLIST_FILE, "w") as f:
        json.dump([], f)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

def load_waitlist() -> List[Dict[str, Any]]:
    """Load the waitlist data."""
    try:
        with open(WAITLIST_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_to_waitlist(subscriber: Dict[str, Any]) -> bool:
    """Save a subscriber to the waitlist."""
    try:
        waitlist = load_waitlist()
        # Check if email already exists
        for entry in waitlist:
            if entry.get("email") == subscriber.get("email"):
                return False
        
        waitlist.append(subscriber)
        
        with open(WAITLIST_FILE, "w") as f:
            json.dump(waitlist, f, indent=2)
        return True
    except Exception:
        return False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request}
    )

@app.get("/api-docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    """Render the API documentation page."""
    return templates.TemplateResponse(
        "api-docs.html", 
        {"request": request}
    )

@app.get("/technology", response_class=HTMLResponse)
async def technology(request: Request):
    """Render the technology page."""
    return templates.TemplateResponse(
        "technology.html", 
        {"request": request}
    )

@app.get("/use-cases", response_class=HTMLResponse)
async def use_cases(request: Request):
    """Render the use cases page."""
    return templates.TemplateResponse(
        "use-cases.html", 
        {"request": request}
    )

@app.get("/waitlist", response_class=HTMLResponse)
async def waitlist(request: Request):
    """Render the waitlist page."""
    return templates.TemplateResponse(
        "waitlist.html", 
        {"request": request}
    )

@app.post("/api/join-waitlist")
async def join_waitlist(
    email: str = Form(...),
    company: str = Form(...),
    use_case: str = Form(...)
):
    """Add a user to the waitlist."""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    if not company:
        raise HTTPException(status_code=400, detail="Company name is required")
    
    subscriber = {
        "id": str(uuid.uuid4()),
        "email": email,
        "company": company,
        "use_case": use_case,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    success = save_to_waitlist(subscriber)
    
    if success:
        return {"success": True, "message": "Thank you for joining our waitlist! We'll be in touch soon with access details."}
    else:
        return {"success": False, "message": "You're already on our waitlist. We'll be in touch soon!"}

@app.get("/api/waitlist-count")
async def waitlist_count():
    """Get the waitlist count."""
    waitlist = load_waitlist()
    return {"count": len(waitlist)}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("Serving LLMRank.io frontend at http://0.0.0.0:4000")
    uvicorn.run(app, host="0.0.0.0", port=4000)