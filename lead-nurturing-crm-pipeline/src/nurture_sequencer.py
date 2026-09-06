"""
Triggers email nurture sequences via a SendGrid-shaped transactional email API.

Swap the endpoint/payload shape in `_send_request` for your actual ESP
(Mailchimp, ActiveCampaign, Customer.io, etc.) without touching the rest of
the pipeline.
"""

import requests

from src.config import Settings
from src.lead_parser import Lead

# Maps our internal sequence names to the ESP's template/automation IDs.
SEQUENCE_TEMPLATE_IDS = {
    "warm_nurture_sequence_b": "d-warm-sequence-template-id",
    "cold_nurture_sequence_a": "d-cold-sequence-template-id",
}


def enroll_in_sequence(settings: Settings, lead: Lead, sequence_name: str) -> dict:
    """Enroll a lead in the given nurture sequence. Returns the ESP's response."""
    template_id = SEQUENCE_TEMPLATE_IDS.get(sequence_name)
    if not template_id:
        raise ValueError(f"Unknown nurture sequence: {sequence_name}")

    response = requests.post(
        "https://api.sendgrid.com/v3/marketing/contacts",
        headers={
            "Authorization": f"Bearer {settings.email_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "contacts": [
                {
                    "email": lead.email,
                    "first_name": lead.name.split(" ")[0] if lead.name else "",
                    "custom_fields": {"nurture_sequence": sequence_name},
                }
            ],
            "list_ids": [template_id],
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json() if response.content else {}
