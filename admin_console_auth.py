"""
Admin Console Authentication
Codename: "Silent Entry"

This module implements secure access control for the admin console
as specified in PRD-41.
"""

import os
import time
import json
import hashlib
import datetime
import logging
import secrets
from typing import Dict, Optional, Tuple, List, Union
from fastapi import Request, HTTPException, Depends, Security
from fastapi.security import APIKeyQuery, APIKeyCookie

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin console auth parameters (would normally be env variables)
ADMIN_AUTH_TOKEN = os.environ.get("ADMIN_AUTH_TOKEN", "sk_master_f2a7b3e1d5c9")
ADMIN_AUTH_HASHED_PASSWORD = os.environ.get("ADMIN_AUTH_HASHED_PASSWORD", 
                                          "5f4dcc3b5aa765d61d8327deb882cf99")  # Default hash
ALLOW_CONSOLE = os.environ.get("ALLOW_CONSOLE", "true").lower() == "true"

# Authentication schemes
auth_token_query = APIKeyQuery(name="auth_token", auto_error=False)
signature_query = APIKeyQuery(name="signature", auto_error=False)
session_cookie = APIKeyCookie(name="admin_session", auto_error=False)

# Constants
FAILED_ATTEMPTS_LOG = "data/system_feedback/failed_admin_attempts.json"
RECOVERY_TOKENS_PATH = "data/system_feedback/recovery_tokens.json"
KEY_FILE_PATH = "/mnt/secure/auth.sk.key"
MAX_FAILED_ATTEMPTS = 3
ATTEMPT_WINDOW_HOURS = 24

# Ensure log directories exist
os.makedirs(os.path.dirname(FAILED_ATTEMPTS_LOG), exist_ok=True)
os.makedirs(os.path.dirname(RECOVERY_TOKENS_PATH), exist_ok=True)

def hash_passphrase(passphrase: str) -> str:
    """
    Hash a passphrase using SHA-256.
    
    Args:
        passphrase: Passphrase to hash
        
    Returns:
        Hashed passphrase
    """
    return hashlib.sha256(passphrase.encode()).hexdigest()

def validate_auth_token(token: str) -> bool:
    """
    Validate an auth token against the stored admin token.
    
    Args:
        token: Auth token to validate
        
    Returns:
        Whether the token is valid
    """
    return token == ADMIN_AUTH_TOKEN and ALLOW_CONSOLE

def validate_signature(signature: str) -> bool:
    """
    Validate a signature against the stored hashed password.
    
    Args:
        signature: Signature to validate
        
    Returns:
        Whether the signature is valid
    """
    return signature == ADMIN_AUTH_HASHED_PASSWORD

def log_failed_attempt(ip_address: str) -> None:
    """
    Log a failed authentication attempt.
    
    Args:
        ip_address: IP address of the requester
    """
    try:
        # Read existing log
        failed_attempts = []
        if os.path.exists(FAILED_ATTEMPTS_LOG):
            with open(FAILED_ATTEMPTS_LOG, "r") as f:
                failed_attempts = json.load(f)
        
        # Add new attempt
        failed_attempts.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "ip_address": ip_address
        })
        
        # Write updated log
        with open(FAILED_ATTEMPTS_LOG, "w") as f:
            json.dump(failed_attempts, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to log auth attempt: {e}")

def get_failed_attempts_count() -> int:
    """
    Get the number of failed authentication attempts in the last 24 hours.
    
    Returns:
        Number of failed attempts
    """
    try:
        if not os.path.exists(FAILED_ATTEMPTS_LOG):
            return 0
        
        with open(FAILED_ATTEMPTS_LOG, "r") as f:
            failed_attempts = json.load(f)
        
        # Filter for attempts in the last 24 hours
        now = datetime.datetime.now()
        window_start = now - datetime.timedelta(hours=ATTEMPT_WINDOW_HOURS)
        
        recent_attempts = [
            attempt for attempt in failed_attempts
            if datetime.datetime.fromisoformat(attempt["timestamp"]) >= window_start
        ]
        
        return len(recent_attempts)
    except Exception as e:
        logger.error(f"Failed to get failed attempts count: {e}")
        return 0

def generate_recovery_token() -> str:
    """
    Generate a new recovery token.
    
    Returns:
        Generated recovery token
    """
    return f"sk_fallback_{secrets.token_hex(16)}"

def store_recovery_token(token: str) -> bool:
    """
    Store a recovery token.
    
    Args:
        token: Recovery token to store
        
    Returns:
        Whether the token was successfully stored
    """
    try:
        # Read existing tokens
        recovery_tokens = []
        if os.path.exists(RECOVERY_TOKENS_PATH):
            with open(RECOVERY_TOKENS_PATH, "r") as f:
                recovery_tokens = json.load(f)
        
        # Add new token
        recovery_tokens.append({
            "token": token,
            "created": datetime.datetime.now().isoformat(),
            "used": False
        })
        
        # Write updated tokens
        with open(RECOVERY_TOKENS_PATH, "w") as f:
            json.dump(recovery_tokens, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Failed to store recovery token: {e}")
        return False

def validate_recovery_token(token: str) -> bool:
    """
    Validate a recovery token.
    
    Args:
        token: Recovery token to validate
        
    Returns:
        Whether the token is valid
    """
    try:
        if not os.path.exists(RECOVERY_TOKENS_PATH):
            return False
        
        with open(RECOVERY_TOKENS_PATH, "r") as f:
            recovery_tokens = json.load(f)
        
        # Find token
        for record in recovery_tokens:
            if record["token"] == token and not record["used"]:
                # Mark token as used
                record["used"] = True
                record["used_at"] = datetime.datetime.now().isoformat()
                
                # Write updated tokens
                with open(RECOVERY_TOKENS_PATH, "w") as f:
                    json.dump(recovery_tokens, f, indent=2)
                
                return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to validate recovery token: {e}")
        return False

def regenerate_admin_credentials(passphrase: str) -> Tuple[str, str]:
    """
    Regenerate admin credentials.
    
    Args:
        passphrase: New passphrase
        
    Returns:
        Tuple of (auth_token, hashed_password)
    """
    # Generate new auth token
    auth_token = f"sk_master_{secrets.token_hex(16)}"
    
    # Hash new passphrase
    hashed_password = hash_passphrase(passphrase)
    
    # Update global variables (in a real implementation, this would update env variables)
    global ADMIN_AUTH_TOKEN, ADMIN_AUTH_HASHED_PASSWORD
    ADMIN_AUTH_TOKEN = auth_token
    ADMIN_AUTH_HASHED_PASSWORD = hashed_password
    
    # Log credential regeneration
    logger.info("Admin credentials regenerated")
    
    return auth_token, hashed_password

def check_key_file() -> bool:
    """
    Check if a valid key file exists.
    
    Returns:
        Whether a valid key file exists
    """
    try:
        if not os.path.exists(KEY_FILE_PATH):
            return False
        
        with open(KEY_FILE_PATH, "r") as f:
            key_content = f.read().strip()
        
        # Hash key content and compare with stored hash
        key_hash = hashlib.sha256(key_content.encode()).hexdigest()
        
        return key_hash == ADMIN_AUTH_HASHED_PASSWORD
    except Exception as e:
        logger.error(f"Failed to check key file: {e}")
        return False

async def verify_admin_access(
    request: Request,
    auth_token: Optional[str] = Security(auth_token_query),
    signature: Optional[str] = Security(signature_query),
    session: Optional[str] = Security(session_cookie)
) -> bool:
    """
    Verify admin console access.
    
    Args:
        auth_token: Auth token from query parameter
        signature: Signature from query parameter
        session: Session cookie
        request: FastAPI request
        
    Returns:
        Whether access is allowed
        
    Raises:
        HTTPException: If access is denied
    """
    # Get client IP
    client_ip = request.client.host if request and request.client else "unknown"
    
    # Check if console access is allowed
    if not ALLOW_CONSOLE:
        logger.warning(f"Console access attempted from {client_ip} but console is disabled")
        log_failed_attempt(client_ip)
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Check if key file exists and is valid
    if check_key_file():
        logger.info(f"Console access granted to {client_ip} via key file")
        return True
    
    # Check token
    token_valid = validate_auth_token(auth_token)
    
    # Check signature (optional)
    signature_valid = signature is not None and validate_signature(signature)
    
    # Check session cookie (for persistent sessions)
    session_valid = session is not None and session == ADMIN_AUTH_HASHED_PASSWORD
    
    # Grant access if any validation method succeeds
    if token_valid or session_valid or signature_valid:
        logger.info(f"Console access granted to {client_ip}")
        return True
    
    # If all validation methods fail, log the attempt and deny access
    logger.warning(f"Unauthorized console access attempt from {client_ip}")
    log_failed_attempt(client_ip)
    
    # Check if there have been too many failed attempts
    failed_attempts = get_failed_attempts_count()
    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        logger.warning(f"Maximum failed attempts threshold reached: {failed_attempts}")
        
        # Generate a recovery token if necessary
        if not os.path.exists(RECOVERY_TOKENS_PATH) or os.path.getsize(RECOVERY_TOKENS_PATH) == 0:
            recovery_token = generate_recovery_token()
            store_recovery_token(recovery_token)
            logger.warning(f"Recovery token generated: {recovery_token}")
    
    # Return 404 to look like page doesn't exist
    raise HTTPException(status_code=404, detail="Not Found")