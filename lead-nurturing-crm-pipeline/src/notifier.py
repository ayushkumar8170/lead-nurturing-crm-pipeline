"""
Notifies sales reps instantly via a Slack incoming webhook when a hot lead
comes in. Swap for email/SMS by replacing `notify_sales_rep`'s implementation.
"""

import requests

from src.config import Settings
from src.lead_parser import Lead


def notify_sales_rep(settings: Settings, lead: Lead, score: int, reasons: list[str]) -> None:
    reason_lines = "\n".join(f"- {r}" for r in reasons)
    text = (
        f":fire: *Hot lead just came in* (score: {score})\n"
        f"*Name:* {lead.name or 'unknown'}\n"
        f"*Email:* {lead.email}\n"
        f"*Company:* {lead.company or 'unknown'}\n"
        f"*Source:* {lead.source}\n"
        f"*Scoring breakdown:*\n{reason_lines}"
    )

    response = requests.post(
        settings.slack_webhook_url,
        json={"text": text},
        timeout=10,
    )
    response.raise_for_status()
