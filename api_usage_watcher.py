"""
API Usage Watcher Agent

This module implements the api_usage_watcher agent for LLMRank.io's MCP API
as specified in the V2 API Key Lifecycle document (Signal with Security).

The agent monitors API usage patterns to detect abuse, suspicious activity,
and enforce policy rules.
"""

import os
import json
import time
import logging
import datetime
import threading
import statistics
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict

# Import from local modules
from api_key_manager import get_key_manager, get_api_key, get_all_keys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIUsageWatcher:
    """
    Monitors API usage for suspicious patterns and enforces security policies.
    Implements Phase 4 of the V2 API Key Lifecycle (Ongoing Monitoring).
    """
    
    def __init__(self):
        """Initialize the API usage watcher."""
        self.data_dir = os.path.join("data", "api_keys")
        self.alerts_file = os.path.join(self.data_dir, "api_key_alerts.json")
        self.access_log_file = os.path.join(self.data_dir, "api_access_log.json")
        self.ip_tracking_file = os.path.join(self.data_dir, "ip_tracking.json")
        self.monitor_thread = None
        self.last_check = time.time()
        self.alerts = []
        self.ip_tracking = defaultdict(list)
        self.burner_domains = set([
            "mailinator.com",
            "tempmail.com",
            "10minutemail.com",
            "guerrillamail.com",
            "throwawaymail.com",
            "yopmail.com",
            "temp-mail.org"
        ])
        
        # Ensure directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data
        self._load_data()
        
        logger.info("API usage watcher initialized")
    
    def start_monitoring(self, interval: int = 600):
        """
        Start the monitoring thread.
        
        Args:
            interval: Monitoring interval in seconds (default: 10 minutes)
        """
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            logger.info("Monitoring thread already running")
            return
        
        def monitor_loop():
            """Monitoring loop to check API usage."""
            while True:
                try:
                    self.check_api_usage()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Shorter sleep on error
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"API usage monitoring started (interval: {interval}s)")
    
    def _load_data(self):
        """Load existing alerts and IP tracking data."""
        try:
            # Load alerts
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, "r") as f:
                    self.alerts = json.load(f)
            
            # Load IP tracking
            if os.path.exists(self.ip_tracking_file):
                with open(self.ip_tracking_file, "r") as f:
                    ip_data = json.load(f)
                    # Convert to defaultdict
                    self.ip_tracking = defaultdict(list, ip_data)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save alerts and IP tracking data."""
        try:
            # Save alerts
            with open(self.alerts_file, "w") as f:
                json.dump(self.alerts, f, indent=2)
            
            # Save IP tracking
            with open(self.ip_tracking_file, "w") as f:
                json.dump(dict(self.ip_tracking), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def log_api_access(self, token: str, endpoint: str, ip_address: str, status_code: int):
        """
        Log an API access event.
        
        Args:
            token: API key token
            endpoint: API endpoint accessed
            ip_address: Client IP address
            status_code: HTTP status code
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "token": token,
                "endpoint": endpoint,
                "ip_address": ip_address,
                "status_code": status_code
            }
            
            # Update key's last IP and usage count
            key = get_api_key(token)
            if key:
                key["last_ip"] = ip_address
                key["last_used"] = log_entry["timestamp"]
                key["usage_count"] = key.get("usage_count", 0) + 1
            
            # Track IP address
            if ip_address:
                self.ip_tracking[ip_address].append({
                    "timestamp": log_entry["timestamp"],
                    "token": token,
                    "endpoint": endpoint
                })
                
                # Keep only the last 100 events per IP
                if len(self.ip_tracking[ip_address]) > 100:
                    self.ip_tracking[ip_address] = self.ip_tracking[ip_address][-100:]
            
            # Append to access log
            access_logs = []
            if os.path.exists(self.access_log_file):
                try:
                    with open(self.access_log_file, "r") as f:
                        access_logs = json.load(f)
                except json.JSONDecodeError:
                    access_logs = []
            
            access_logs.append(log_entry)
            
            # Keep only the last 1000 access logs
            if len(access_logs) > 1000:
                access_logs = access_logs[-1000:]
            
            with open(self.access_log_file, "w") as f:
                json.dump(access_logs, f, indent=2)
            
            # Save IP tracking
            self._save_data()
        except Exception as e:
            logger.error(f"Error logging API access: {e}")
    
    def check_api_usage(self):
        """
        Check API usage for suspicious patterns and enforce security policies.
        This is the main monitoring function that implements Phase 4 of the V2 lifecycle.
        """
        now = time.time()
        self.last_check = now
        
        logger.info("Checking API usage patterns...")
        
        try:
            # Get all keys
            all_keys = get_all_keys()
            
            # Check for expired temporary keys
            self._check_expired_keys(all_keys)
            
            # Check for suspicious usage patterns
            self._check_usage_spikes(all_keys)
            
            # Check for IP drift (key sharing)
            self._check_ip_drift(all_keys)
            
            # Check for suspicious endpoint access patterns
            self._check_endpoint_patterns()
            
            # Check for burner domains
            self._check_burner_domains(all_keys)
            
            # Save alerts
            self._save_data()
            
            logger.info("API usage check completed")
        except Exception as e:
            logger.error(f"Error checking API usage: {e}")
    
    def _check_expired_keys(self, keys: List[Dict]):
        """
        Check for and flag expired temporary keys.
        
        Args:
            keys: List of API key dictionaries
        """
        now = datetime.datetime.now().isoformat()
        
        for key in keys:
            if key.get("status") == "active" and key.get("expires") and key.get("plan") == "free_temp":
                # Check if key has expired
                if key["expires"] < now:
                    # Flag the key
                    key["status"] = "expired"
                    key["flagged"] = True
                    key["flag_reason"] = "Temporary key expired"
                    
                    # Add alert
                    self._add_alert(
                        key["token"],
                        "Temporary key expired",
                        "revoke",
                        {
                            "user_id": key.get("user_id"),
                            "email": key.get("email"),
                            "expiration": key.get("expires")
                        }
                    )
                    
                    logger.info(f"Flagged expired temporary key: {key['token']}")
    
    def _check_usage_spikes(self, keys: List[Dict]):
        """
        Check for unusual usage spikes.
        
        Args:
            keys: List of API key dictionaries
        """
        # Load access logs
        access_logs = []
        if os.path.exists(self.access_log_file):
            try:
                with open(self.access_log_file, "r") as f:
                    access_logs = json.load(f)
            except json.JSONDecodeError:
                access_logs = []
        
        # Skip if not enough data
        if len(access_logs) < 10:
            return
        
        # Get current time
        now = datetime.datetime.now()
        
        # Group logs by key and calculate hourly rates
        key_usage = defaultdict(list)
        
        for log in access_logs:
            timestamp = log.get("timestamp", "")
            token = log.get("token", "")
            
            if not timestamp or not token:
                continue
            
            try:
                log_time = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_diff = (now - log_time).total_seconds() / 3600  # Hours
                
                # Only consider events in the last 24 hours
                if time_diff <= 24:
                    key_usage[token].append(log_time)
            except Exception as e:
                logger.error(f"Error parsing timestamp: {e}")
        
        # Check for usage spikes
        for token, timestamps in key_usage.items():
            key = get_api_key(token)
            
            if not key or key.get("status") != "active":
                continue
            
            # Get hourly counts
            hourly_counts = defaultdict(int)
            for ts in timestamps:
                hour_key = ts.strftime("%Y-%m-%d-%H")
                hourly_counts[hour_key] += 1
            
            # Calculate statistics
            if hourly_counts:
                counts = list(hourly_counts.values())
                avg_count = sum(counts) / len(counts)
                
                # Check for spikes
                for hour, count in hourly_counts.items():
                    # Flag if count is more than 5x the average and at least 20 requests
                    if count > max(5 * avg_count, 20):
                        # Flag the key if not already flagged
                        if not key.get("flagged", False):
                            key["flagged"] = True
                            key["flag_reason"] = f"Unusual usage spike: {count} requests in 1 hour"
                            
                            # Add alert
                            self._add_alert(
                                token,
                                "Unusual usage spike detected",
                                "rate_limit",
                                {
                                    "hour": hour,
                                    "count": count,
                                    "average": avg_count,
                                    "plan": key.get("plan")
                                }
                            )
                            
                            logger.info(f"Flagged key for usage spike: {token}")
    
    def _check_ip_drift(self, keys: List[Dict]):
        """
        Check for IP drift (potential key sharing).
        
        Args:
            keys: List of API key dictionaries
        """
        # Load access logs
        access_logs = []
        if os.path.exists(self.access_log_file):
            try:
                with open(self.access_log_file, "r") as f:
                    access_logs = json.load(f)
            except json.JSONDecodeError:
                access_logs = []
        
        # Skip if not enough data
        if len(access_logs) < 10:
            return
        
        # Group logs by key and track IPs
        key_ips = defaultdict(set)
        
        for log in access_logs:
            token = log.get("token", "")
            ip = log.get("ip_address", "")
            
            if token and ip:
                key_ips[token].add(ip)
        
        # Check for IP drift
        for token, ips in key_ips.items():
            key = get_api_key(token)
            
            if not key or key.get("status") != "active":
                continue
            
            # Skip keys with verified status (paid plans)
            if key.get("verified", False) and key.get("plan") not in ["free_temp", "free"]:
                continue
            
            # Flag if key used from more than 3 IPs
            if len(ips) > 3:
                # Flag the key if not already flagged
                if not key.get("flagged", False):
                    key["flagged"] = True
                    key["flag_reason"] = f"Potential key sharing: Used from {len(ips)} different IPs"
                    
                    # Add alert
                    self._add_alert(
                        token,
                        "Potential API key sharing detected",
                        "email_verify",
                        {
                            "ip_count": len(ips),
                            "ips": list(ips),
                            "user_id": key.get("user_id"),
                            "email": key.get("email")
                        }
                    )
                    
                    logger.info(f"Flagged key for IP drift: {token}")
    
    def _check_endpoint_patterns(self):
        """Check for suspicious endpoint access patterns."""
        # Load access logs
        access_logs = []
        if os.path.exists(self.access_log_file):
            try:
                with open(self.access_log_file, "r") as f:
                    access_logs = json.load(f)
            except json.JSONDecodeError:
                access_logs = []
        
        # Skip if not enough data
        if len(access_logs) < 20:
            return
        
        # Get current time
        now = datetime.datetime.now()
        
        # Group recent logs by key
        key_endpoints = defaultdict(list)
        ip_endpoints = defaultdict(list)
        
        for log in access_logs:
            timestamp = log.get("timestamp", "")
            token = log.get("token", "")
            endpoint = log.get("endpoint", "")
            ip = log.get("ip_address", "")
            
            if not timestamp or not token or not endpoint:
                continue
            
            try:
                log_time = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_diff = (now - log_time).total_seconds() / 60  # Minutes
                
                # Only consider events in the last 10 minutes
                if time_diff <= 10:
                    key_endpoints[token].append(endpoint)
                    if ip:
                        ip_endpoints[ip].append(endpoint)
            except Exception as e:
                logger.error(f"Error parsing timestamp: {e}")
        
        # Check for suspicious endpoint access patterns
        for token, endpoints in key_endpoints.items():
            key = get_api_key(token)
            
            if not key or key.get("status") != "active":
                continue
            
            # Check for high endpoint diversity (potential crawler)
            unique_endpoints = set(endpoints)
            if len(unique_endpoints) >= 12 and len(endpoints) >= 30:
                # Flag the key if not already flagged
                if not key.get("flagged", False):
                    key["flagged"] = True
                    key["flag_reason"] = f"Potential crawler: Accessed {len(unique_endpoints)} different endpoints in 10 minutes"
                    
                    # Add alert
                    self._add_alert(
                        token,
                        "Potential crawler detected",
                        "rate_limit",
                        {
                            "endpoint_count": len(unique_endpoints),
                            "request_count": len(endpoints),
                            "plan": key.get("plan")
                        }
                    )
                    
                    logger.info(f"Flagged key for crawler behavior: {token}")
        
        # Check for suspicious IP patterns
        for ip, endpoints in ip_endpoints.items():
            # Check for high endpoint diversity from single IP
            unique_endpoints = set(endpoints)
            if len(unique_endpoints) >= 15 and len(endpoints) >= 40:
                # Add alert for IP
                self._add_alert(
                    "ip_alert",
                    "Suspicious IP activity detected",
                    "ip_ban",
                    {
                        "ip_address": ip,
                        "endpoint_count": len(unique_endpoints),
                        "request_count": len(endpoints)
                    }
                )
                
                logger.info(f"Flagged IP for suspicious activity: {ip}")
    
    def _check_burner_domains(self, keys: List[Dict]):
        """
        Check for keys registered with burner domains.
        
        Args:
            keys: List of API key dictionaries
        """
        for key in keys:
            if key.get("status") != "active" or key.get("flagged", False):
                continue
            
            email = key.get("email", "")
            if not email:
                continue
            
            domain = email.split("@")[-1].lower() if "@" in email else ""
            
            if domain in self.burner_domains:
                # Flag the key
                key["flagged"] = True
                key["flag_reason"] = f"Registered with burner domain: {domain}"
                
                # Add alert
                self._add_alert(
                    key["token"],
                    "Burner email domain detected",
                    "email_verify",
                    {
                        "email": email,
                        "domain": domain,
                        "user_id": key.get("user_id")
                    }
                )
                
                logger.info(f"Flagged key for burner domain: {key['token']}")
    
    def _add_alert(self, token: str, message: str, action: str, details: Dict = None):
        """
        Add an alert.
        
        Args:
            token: API key token or alert identifier
            message: Alert message
            action: Suggested action (revoke, rate_limit, email_verify, ip_ban)
            details: Additional details
        """
        alert = {
            "id": f"alert_{int(time.time())}_{token[:8]}",
            "timestamp": datetime.datetime.now().isoformat(),
            "token": token,
            "message": message,
            "suggested_action": action,
            "details": details or {},
            "resolved": False
        }
        
        self.alerts.append(alert)
        
        # Keep only the last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        logger.info(f"Added alert: {message} for {token}")
    
    def get_alerts(self, include_resolved: bool = False) -> List[Dict]:
        """
        Get alerts.
        
        Args:
            include_resolved: Whether to include resolved alerts
            
        Returns:
            List of alert dictionaries
        """
        if include_resolved:
            return self.alerts
        return [alert for alert in self.alerts if not alert.get("resolved", False)]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Success flag
        """
        for alert in self.alerts:
            if alert.get("id") == alert_id:
                alert["resolved"] = True
                alert["resolved_at"] = datetime.datetime.now().isoformat()
                self._save_data()
                logger.info(f"Resolved alert: {alert_id}")
                return True
        
        logger.warning(f"Alert not found: {alert_id}")
        return False
    
    def get_flagged_keys(self) -> List[Dict]:
        """
        Get flagged API keys.
        
        Returns:
            List of flagged API key dictionaries
        """
        flagged_keys = []
        for key in get_all_keys():
            if key.get("flagged", False):
                flagged_keys.append(key)
        
        return flagged_keys
    
    def unflag_key(self, token: str) -> bool:
        """
        Remove flag from an API key.
        
        Args:
            token: API key token
            
        Returns:
            Success flag
        """
        key = get_api_key(token)
        
        if key and key.get("flagged", False):
            key["flagged"] = False
            key["flag_reason"] = None
            logger.info(f"Unflagged key: {token}")
            return True
        
        logger.warning(f"Key not found or not flagged: {token}")
        return False
    
    def get_suspicious_ips(self) -> List[Dict]:
        """
        Get suspicious IP addresses.
        
        Returns:
            List of suspicious IP dictionaries
        """
        suspicious_ips = []
        
        for ip, events in self.ip_tracking.items():
            if len(events) > 100:
                # Check access patterns
                endpoints = [event.get("endpoint", "") for event in events]
                unique_endpoints = set(endpoints)
                
                # Flag IPs with high request volume and endpoint diversity
                if len(unique_endpoints) > 10 and len(events) > 200:
                    suspicious_ips.append({
                        "ip_address": ip,
                        "event_count": len(events),
                        "unique_endpoints": len(unique_endpoints),
                        "last_seen": events[-1].get("timestamp") if events else ""
                    })
        
        return suspicious_ips

# Singleton instance
_instance = None

def get_api_usage_watcher() -> APIUsageWatcher:
    """Get the API usage watcher singleton instance."""
    global _instance
    
    if _instance is None:
        _instance = APIUsageWatcher()
    
    return _instance

def start_monitoring(interval: int = 600):
    """Start the API usage monitoring."""
    get_api_usage_watcher().start_monitoring(interval)

def log_api_access(token: str, endpoint: str, ip_address: str, status_code: int):
    """Log an API access event."""
    get_api_usage_watcher().log_api_access(token, endpoint, ip_address, status_code)

def check_api_usage():
    """Check API usage patterns."""
    get_api_usage_watcher().check_api_usage()

def get_alerts(include_resolved: bool = False) -> List[Dict]:
    """Get alerts."""
    return get_api_usage_watcher().get_alerts(include_resolved)

def resolve_alert(alert_id: str) -> bool:
    """Resolve an alert."""
    return get_api_usage_watcher().resolve_alert(alert_id)

def get_flagged_keys() -> List[Dict]:
    """Get flagged API keys."""
    return get_api_usage_watcher().get_flagged_keys()

def unflag_key(token: str) -> bool:
    """Remove flag from an API key."""
    return get_api_usage_watcher().unflag_key(token)

def get_suspicious_ips() -> List[Dict]:
    """Get suspicious IP addresses."""
    return get_api_usage_watcher().get_suspicious_ips()