"""
Pushes a lead and its resolved pipeline stage to the CRM via a generic
REST API (HubSpot-shaped). Swap the endpoint/payload for Salesforce,
Pipedrive, etc. without touching the rest of the pipeline.
"""

import requests

from src.config import Settings
from src.lead_parser import Lead
from src.router import LeadStage

# Maps our internal stage names to the CRM's pipeline stage IDs.
CRM_STAGE_IDS = {
    LeadStage.HOT: "stage_sales_qualified",
    LeadStage.WARM: "stage_marketing_nurture",
    LeadStage.COLD: "stage_top_of_funnel",
}


def upsert_lead(settings: Settings, lead: Lead, stage: LeadStage, score: int) -> dict:
    """Create or update the lead record in the CRM with its resolved stage."""
    payload = {
        "properties": {
            "email": lead.email,
            "firstname": lead.name.split(" ")[0] if lead.name else "",
            "lastname": " ".join(lead.name.split(" ")[1:]) if lead.name else "",
            "phone": lead.phone,
            "company": lead.company,
            "jobtitle": lead.job_title,
            "lead_source": lead.source,
            "lead_score": score,
            "pipeline_stage": CRM_STAGE_IDS[stage],
        }
    }

    response = requests.post(
        f"{settings.crm_api_base_url}/crm/v3/objects/contacts",
        headers={
            "Authorization": f"Bearer {settings.crm_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    return response.json() if response.content else {}
