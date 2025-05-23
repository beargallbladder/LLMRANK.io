"""
Notification Agent

This module implements the notification system for the LLMRank Insight Engine.
It sends alerts to Slack, email, and other channels when domains experience
significant changes in their ranking across LLMs.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import domain_memory_tracker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_ALERTS_PER_BATCH = 10
NOTIFICATION_COOLDOWN_HOURS = 24  # Don't send repeated alerts for same domain within this period

# File paths
DATA_DIR = "data/notifications"
os.makedirs(DATA_DIR, exist_ok=True)

NOTIFICATION_CONFIG_PATH = os.path.join(DATA_DIR, "notification_config.json")
NOTIFICATION_HISTORY_PATH = os.path.join(DATA_DIR, "notification_history.json")

# Default emoji mappings
DEFAULT_EMOJI_MAP = {
    "improvement_large": "🚀",    # Rank improved by >5
    "improvement_medium": "📈",   # Rank improved by 3-5
    "improvement_small": "⬆️",    # Rank improved by 1-2
    "decline_large": "📉",        # Rank declined by >5
    "decline_medium": "⬇️",       # Rank declined by 3-5
    "decline_small": "🔽",        # Rank declined by 1-2
    "new_entry": "🆕",            # New entry to rankings
    "dropped_out": "❌"           # Dropped out of rankings
}


class NotificationAgent:
    """
    Handles notifications for significant domain ranking changes across
    various channels like Slack, email, etc.
    """
    
    def __init__(self):
        """Initialize the notification agent."""
        self.notification_config = {
            "slack_webhooks": {},  # domain or "default" -> webhook URL
            "email_recipients": {},  # domain or "default" -> list of email addresses
            "notification_threshold": 3,  # Minimum delta to trigger notification
            "channels_enabled": {
                "slack": False,
                "email": False,
                "dashboard": True,
                "api": True
            },
            "emoji_map": DEFAULT_EMOJI_MAP
        }
        
        self.notification_history = []  # List of sent notifications
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing data from files."""
        try:
            if os.path.exists(NOTIFICATION_CONFIG_PATH):
                with open(NOTIFICATION_CONFIG_PATH, 'r') as f:
                    self.notification_config = json.load(f)
                    
            if os.path.exists(NOTIFICATION_HISTORY_PATH):
                with open(NOTIFICATION_HISTORY_PATH, 'r') as f:
                    self.notification_history = json.load(f)
                    
            logger.info("Notification data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading notification data: {e}")
            # Use default configuration
            pass
    
    def _save_data(self):
        """Save current data to files."""
        try:
            # Save notification config
            with open(NOTIFICATION_CONFIG_PATH, 'w') as f:
                json.dump(self.notification_config, f, indent=2)
                
            # Save notification history
            with open(NOTIFICATION_HISTORY_PATH, 'w') as f:
                json.dump(self.notification_history, f, indent=2)
                
            logger.info("Notification data saved successfully")
        except Exception as e:
            logger.error(f"Error saving notification data: {e}")
    
    def configure_slack(self, webhook_url: str, domain: Optional[str] = "default"):
        """
        Configure Slack webhook URL for notifications.
        
        Args:
            webhook_url: Slack webhook URL
            domain: Optional domain to configure for, or "default" for all domains
            
        Returns:
            Success flag
        """
        self.notification_config["slack_webhooks"][domain] = webhook_url
        self.notification_config["channels_enabled"]["slack"] = True
        
        self._save_data()
        logger.info(f"Configured Slack webhook for {domain}")
        
        return True
    
    def configure_email(self, email_addresses: List[str], domain: Optional[str] = "default"):
        """
        Configure email recipients for notifications.
        
        Args:
            email_addresses: List of email addresses
            domain: Optional domain to configure for, or "default" for all domains
            
        Returns:
            Success flag
        """
        self.notification_config["email_recipients"][domain] = email_addresses
        self.notification_config["channels_enabled"]["email"] = True
        
        self._save_data()
        logger.info(f"Configured email recipients for {domain}")
        
        return True
    
    def set_notification_threshold(self, threshold: int):
        """
        Set the minimum delta threshold for triggering notifications.
        
        Args:
            threshold: Minimum delta to trigger notification
            
        Returns:
            Success flag
        """
        self.notification_config["notification_threshold"] = max(1, threshold)
        
        self._save_data()
        logger.info(f"Set notification threshold to {threshold}")
        
        return True
    
    def enable_channel(self, channel: str, enabled: bool = True):
        """
        Enable or disable a notification channel.
        
        Args:
            channel: Channel name ("slack", "email", "dashboard", "api")
            enabled: Whether to enable or disable the channel
            
        Returns:
            Success flag
        """
        if channel not in self.notification_config["channels_enabled"]:
            return False
            
        self.notification_config["channels_enabled"][channel] = enabled
        
        self._save_data()
        logger.info(f"{'Enabled' if enabled else 'Disabled'} {channel} notifications")
        
        return True
    
    def customize_emoji(self, event_type: str, emoji: str):
        """
        Customize emoji for notification events.
        
        Args:
            event_type: Event type 
            emoji: Emoji to use for the event
            
        Returns:
            Success flag
        """
        if event_type not in self.notification_config["emoji_map"]:
            return False
            
        self.notification_config["emoji_map"][event_type] = emoji
        
        self._save_data()
        logger.info(f"Customized emoji for {event_type} to {emoji}")
        
        return True
    
    def _get_emoji_for_delta(self, delta: int) -> str:
        """
        Get the appropriate emoji for a given delta.
        
        Args:
            delta: Rank change delta (positive means improvement)
            
        Returns:
            Emoji string
        """
        emoji_map = self.notification_config["emoji_map"]
        
        if delta > 0:
            if delta > 5:
                return emoji_map["improvement_large"]
            elif delta >= 3:
                return emoji_map["improvement_medium"]
            else:
                return emoji_map["improvement_small"]
        else:
            delta = abs(delta)
            if delta > 5:
                return emoji_map["decline_large"]
            elif delta >= 3:
                return emoji_map["decline_medium"]
            else:
                return emoji_map["decline_small"]
    
    def _format_slack_message(self, alert: Dict) -> Dict:
        """
        Format an alert as a Slack message.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Formatted Slack message dictionary
        """
        delta = alert["delta"]
        emoji = self._get_emoji_for_delta(delta)
        
        # Determine color based on delta
        color = "#36a64f" if delta > 0 else "#d00000"  # Green for improvements, red for declines
        
        # Format delta as string with sign
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        
        # Create message text
        domain = alert["domain"]
        model = alert["model"]
        query_category = alert["query_category"]
        previous_rank = alert["previous_rank"]
        current_rank = alert["current_rank"]
        
        message = {
            "attachments": [
                {
                    "fallback": f"{domain} rank change alert",
                    "color": color,
                    "pretext": f"{emoji} *Domain Rank Change Alert*",
                    "title": f"{domain}",
                    "title_link": f"https://llmpagerank.com/domain/{domain}",
                    "text": f"*{delta_str}* rank change detected in *{model}* for category *{query_category}*\n"
                           f"Previous rank: {previous_rank} → Current rank: {current_rank}",
                    "fields": [
                        {
                            "title": "Model",
                            "value": model,
                            "short": True
                        },
                        {
                            "title": "Category",
                            "value": query_category,
                            "short": True
                        },
                        {
                            "title": "Previous Rank",
                            "value": previous_rank,
                            "short": True
                        },
                        {
                            "title": "Current Rank",
                            "value": current_rank,
                            "short": True
                        }
                    ],
                    "footer": "LLMPageRank Insight Engine",
                    "footer_icon": "https://llmpagerank.com/favicon.ico",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return message
    
    def _send_slack_notification(self, alert: Dict) -> bool:
        """
        Send a Slack notification for an alert.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Success flag
        """
        domain = alert["domain"]
        
        # Get webhook URL for this domain or fall back to default
        webhook_url = self.notification_config["slack_webhooks"].get(
            domain, 
            self.notification_config["slack_webhooks"].get("default")
        )
        
        if not webhook_url:
            logger.warning(f"No Slack webhook configured for {domain}")
            return False
        
        # Format message
        message = self._format_slack_message(alert)
        
        try:
            response = requests.post(
                webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Sent Slack notification for {domain}")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def _format_email_message(self, alert: Dict) -> Dict:
        """
        Format an alert as an email message.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Formatted email message dictionary
        """
        delta = alert["delta"]
        emoji = self._get_emoji_for_delta(delta)
        
        # Format delta as string with sign
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        
        # Create message text
        domain = alert["domain"]
        model = alert["model"]
        query_category = alert["query_category"]
        previous_rank = alert["previous_rank"]
        current_rank = alert["current_rank"]
        
        subject = f"{emoji} LLMPageRank Alert: {domain} {delta_str} rank change"
        
        body = f"""
        <h2>{emoji} Domain Rank Change Alert</h2>
        
        <p><strong>{domain}</strong> has experienced a rank change of <strong>{delta_str}</strong>
        in <strong>{model}</strong> for category <strong>{query_category}</strong>.</p>
        
        <p>Previous rank: {previous_rank} → Current rank: {current_rank}</p>
        
        <p>View more details at: <a href="https://llmpagerank.com/domain/{domain}">LLMPageRank Dashboard</a></p>
        
        <hr>
        <p><small>LLMPageRank Insight Engine</small></p>
        """
        
        return {
            "subject": subject,
            "body": body
        }
    
    def _send_email_notification(self, alert: Dict) -> bool:
        """
        Send an email notification for an alert.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Success flag
        """
        # NOTE: In a production system, this would use an email API service
        # For the prototype, we'll just log the email content
        
        domain = alert["domain"]
        
        # Get email recipients for this domain or fall back to default
        recipients = self.notification_config["email_recipients"].get(
            domain, 
            self.notification_config["email_recipients"].get("default", [])
        )
        
        if not recipients:
            logger.warning(f"No email recipients configured for {domain}")
            return False
        
        # Format message
        message = self._format_email_message(alert)
        
        # Log email content
        logger.info(f"Would send email notification for {domain} to {recipients}:")
        logger.info(f"Subject: {message['subject']}")
        logger.info(f"Body: {message['body']}")
        
        # In a real implementation, this would use an email API service
        return True
    
    def check_for_alerts(self) -> int:
        """
        Check for new alerts and send notifications.
        
        Returns:
            Number of notifications sent
        """
        # Get unnotified alerts
        alerts = domain_memory_tracker.get_significant_deltas(days=1)
        
        unnotified_alerts = [
            alert for alert in alerts 
            if not alert.get("notified", False)
        ]
        
        if not unnotified_alerts:
            logger.info("No new alerts to notify")
            return 0
        
        logger.info(f"Found {len(unnotified_alerts)} unnotified alerts")
        
        # Apply notification threshold
        threshold = self.notification_config["notification_threshold"]
        threshold_filtered_alerts = [
            alert for alert in unnotified_alerts
            if abs(alert["delta"]) >= threshold
        ]
        
        logger.info(f"{len(threshold_filtered_alerts)} alerts meet threshold {threshold}")
        
        # Apply cooldown filter
        cooldown_filtered_alerts = self._filter_by_cooldown(threshold_filtered_alerts)
        
        logger.info(f"{len(cooldown_filtered_alerts)} alerts after cooldown filter")
        
        # Limit batch size
        alerts_to_notify = cooldown_filtered_alerts[:MAX_ALERTS_PER_BATCH]
        
        # Send notifications
        sent_count = 0
        alert_ids = []
        
        for alert in alerts_to_notify:
            success = self._send_notification(alert)
            
            if success:
                # Add to notification history
                self._record_notification(alert)
                
                # Mark as notified
                alert_ids.append(alert["timestamp"])
                
                sent_count += 1
        
        # Update alerts as notified
        if alert_ids:
            domain_memory_tracker.get_tracker().mark_alerts_as_notified(alert_ids)
        
        logger.info(f"Sent {sent_count} notifications")
        
        return sent_count
    
    def _filter_by_cooldown(self, alerts: List[Dict]) -> List[Dict]:
        """
        Filter alerts by notification cooldown period.
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Filtered list of alerts
        """
        # Calculate cooldown timestamp
        cooldown_time = datetime.now() - timedelta(hours=NOTIFICATION_COOLDOWN_HOURS)
        cooldown_timestamp = cooldown_time.isoformat()
        
        # Get domains notified recently
        recently_notified_domains = set()
        
        for notification in self.notification_history:
            if notification["timestamp"] >= cooldown_timestamp:
                recently_notified_domains.add(notification["domain"])
        
        # Filter alerts
        return [
            alert for alert in alerts
            if alert["domain"] not in recently_notified_domains
        ]
    
    def _send_notification(self, alert: Dict) -> bool:
        """
        Send a notification for an alert through all enabled channels.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Success flag (True if sent through at least one channel)
        """
        channels_enabled = self.notification_config["channels_enabled"]
        success = False
        
        # Send through enabled channels
        if channels_enabled.get("slack", False):
            slack_success = self._send_slack_notification(alert)
            success = success or slack_success
        
        if channels_enabled.get("email", False):
            email_success = self._send_email_notification(alert)
            success = success or email_success
        
        # Dashboard and API notifications are always marked as successful
        # as they don't involve external services
        if channels_enabled.get("dashboard", True) or channels_enabled.get("api", True):
            success = True
        
        return success
    
    def _record_notification(self, alert: Dict):
        """
        Record a sent notification in history.
        
        Args:
            alert: Alert dictionary
        """
        notification = {
            "timestamp": datetime.now().isoformat(),
            "domain": alert["domain"],
            "model": alert["model"],
            "query_category": alert["query_category"],
            "delta": alert["delta"],
            "previous_rank": alert["previous_rank"],
            "current_rank": alert["current_rank"]
        }
        
        self.notification_history.append(notification)
        
        # Trim history (keep last 1000)
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
            
        self._save_data()
    
    def get_notification_history(self, domain: Optional[str] = None, 
                              days: int = 7, limit: int = 100) -> List[Dict]:
        """
        Get notification history, optionally filtered by domain.
        
        Args:
            domain: Optional domain filter
            days: Number of days to look back
            limit: Maximum number of entries to return
            
        Returns:
            List of notification dictionaries
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Filter history
        filtered_history = []
        
        for notification in self.notification_history:
            if notification["timestamp"] < cutoff_date:
                continue
                
            if domain and notification["domain"] != domain:
                continue
                
            filtered_history.append(notification)
        
        # Sort by timestamp (newest first)
        sorted_history = sorted(filtered_history, 
                             key=lambda x: x["timestamp"], 
                             reverse=True)
        
        return sorted_history[:limit]


# Singleton instance
_notification_agent = None

def get_agent() -> NotificationAgent:
    """Get the notification agent singleton instance."""
    global _notification_agent
    
    if _notification_agent is None:
        _notification_agent = NotificationAgent()
    
    return _notification_agent

def configure_slack(webhook_url: str, domain: Optional[str] = "default") -> bool:
    """
    Configure Slack webhook URL for notifications.
    
    Args:
        webhook_url: Slack webhook URL
        domain: Optional domain to configure for, or "default" for all domains
        
    Returns:
        Success flag
    """
    return get_agent().configure_slack(webhook_url, domain)

def configure_email(email_addresses: List[str], domain: Optional[str] = "default") -> bool:
    """
    Configure email recipients for notifications.
    
    Args:
        email_addresses: List of email addresses
        domain: Optional domain to configure for, or "default" for all domains
        
    Returns:
        Success flag
    """
    return get_agent().configure_email(email_addresses, domain)

def set_notification_threshold(threshold: int) -> bool:
    """
    Set the minimum delta threshold for triggering notifications.
    
    Args:
        threshold: Minimum delta to trigger notification
        
    Returns:
        Success flag
    """
    return get_agent().set_notification_threshold(threshold)

def enable_channel(channel: str, enabled: bool = True) -> bool:
    """
    Enable or disable a notification channel.
    
    Args:
        channel: Channel name ("slack", "email", "dashboard", "api")
        enabled: Whether to enable or disable the channel
        
    Returns:
        Success flag
    """
    return get_agent().enable_channel(channel, enabled)

def customize_emoji(event_type: str, emoji: str) -> bool:
    """
    Customize emoji for notification events.
    
    Args:
        event_type: Event type 
        emoji: Emoji to use for the event
        
    Returns:
        Success flag
    """
    return get_agent().customize_emoji(event_type, emoji)

def check_for_alerts() -> int:
    """
    Check for new alerts and send notifications.
    
    Returns:
        Number of notifications sent
    """
    return get_agent().check_for_alerts()

def get_notification_history(domain: Optional[str] = None, 
                          days: int = 7, limit: int = 100) -> List[Dict]:
    """
    Get notification history, optionally filtered by domain.
    
    Args:
        domain: Optional domain filter
        days: Number of days to look back
        limit: Maximum number of entries to return
        
    Returns:
        List of notification dictionaries
    """
    return get_agent().get_notification_history(domain, days, limit)