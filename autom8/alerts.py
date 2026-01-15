# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

alerts.py - Alert System
Sends email notifications on critical events
in the Autom8 system.
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from pathlib import Path
from autom8.core import log

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True") == "True"
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

# Template Caching
_TEMPLATE_CACHE = None


def _get_alert_template():
    """Load and cache the HTML alert template."""
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return _TEMPLATE_CACHE

    template_path = Path(__file__).parent / "templates" / "alert_email.html"
    try:
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                _TEMPLATE_CACHE = Template(f.read())
            return _TEMPLATE_CACHE
    except Exception as e:
        log.error(f"Error loading alert template: {e}")

    # Minimal fallback template if file missing
    return Template("<html><body><h2>Alert</h2><p>${task_type}: ${error_message}</p></body></html>")


# Alert functions
def send_email_alert(subject, body, to_email=None):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        log.warning("Email credentials not set. Skipping email alert.")
        return False

    try:
        to_email = to_email or ALERT_EMAIL

        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = f"[AUTOM8 ALERT] {subject}"

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())

        log.info(f"Email alert sent to {to_email}: {subject}")
        return True

    except Exception as e:
        log.error(f"Error sending email alert: {e}")
        return False


def alert_task_failure(task_type, error_message):
    subject = f"Task Failure: {task_type}"
    template = _get_alert_template()
    body = template.substitute(
        task_type=task_type,
        error_message=error_message,
        timestamp=datetime.now().isoformat() + "Z",
    )
    send_email_alert(subject, body)


def alert_system_issue(issue_type, details):
    subject = f"System Issue: {issue_type}"
    template = _get_alert_template()
    # Using the same template but mapping labels
    body = template.substitute(
        task_type=issue_type, error_message=details, timestamp=datetime.now().isoformat() + "Z"
    )
    send_email_alert(subject, body)


# Module exports
__all__ = ["send_email_alert", "alert_task_failure", "alert_system_issue"]
