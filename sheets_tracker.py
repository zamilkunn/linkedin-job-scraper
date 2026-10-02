"""
Google Sheets Job Application Tracker Module
Integrates with Google Apps Script Webhook to automatically log applied jobs.
"""

import logging
from urllib.parse import urlencode
import requests

logger = logging.getLogger(__name__)


def generate_tracking_url(webhook_base_url: str, title: str, company: str, location: str, job_url: str) -> str:
    """
    Generate a 1-click tracking URL that logs the application to Google Sheets.
    """
    if not webhook_base_url:
        return ""
        
    params = {
        "action": "apply",
        "title": title,
        "company": company,
        "location": location,
        "url": job_url,
    }
    return f"{webhook_base_url}?{urlencode(params)}"


def log_to_sheets_direct(webhook_base_url: str, title: str, company: str, location: str, job_url: str) -> bool:
    """
    Directly send a POST request to Google Apps Script Webhook.
    """
    if not webhook_base_url:
        return False

    try:
        payload = {
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
        }
        res = requests.post(webhook_base_url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        logger.error(f"Failed to log to Google Sheets: {e}")
        return False
