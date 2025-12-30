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

from autom8.core import log

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True") == "True"
ALERT_EMAIL = os.getenv("ALERT_EMAIL")


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
    body = f"""
    <html>
    <body>
        <h2>Task Execution Failed</h2>
        <p><strong>Task:</strong> {task_type}</p>
        <p><strong>Time:</strong> {datetime.now().isoformat()}Z</p>
        <p><strong>Error:</strong></p>
        <pre>{error_message}</pre>
        <hr>
        <p><em>This is an automated email alert from Autom8 System</em></p>
    </body>
    </html>
    """
    send_email_alert(subject, body)


def alert_system_issue(issue_type, details):
    subject = f"System Issue: {issue_type}"
    body = f"""
    <html>
    <body>
        <h2>System Issue Detected</h2>
        <p><strong>Issue Type:</strong> {issue_type}</p>
        <p><strong>Time:</strong> {datetime.now().isoformat()}Z</p>
        <p><strong>Details:</strong></p>
        <pre>{details}</pre>
        <hr>
        <p><em>Immediate action may be required</em></p>
    </body>
    </html>
    """
    send_email_alert(subject, body)


# Module exports
__all__ = ["send_email_alert", "alert_task_failure", "alert_system_issue"]
