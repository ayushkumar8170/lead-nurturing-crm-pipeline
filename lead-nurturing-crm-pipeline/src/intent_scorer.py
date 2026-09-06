"""
Rule-based lead intent scoring.

Deliberately rule-based rather than a black-box model: sales and marketing need
to see exactly why a lead was scored the way it was, since the score directly
drives whether a rep gets interrupted right now.
"""

from src.lead_parser import Lead

# Points awarded per lead source. Direct/high-intent channels score higher
# than passive channels like organic social.
SOURCE_SCORES = {
    "demo_request": 40,
    "pricing_page": 35,
    "contact_form": 25,
    "webinar": 20,
    "content_download": 10,
    "organic_social": 5,
    "unknown": 5,
}

# Seniority signals in job title suggest budget authority.
SENIOR_TITLE_KEYWORDS = ("ceo", "cto", "cfo", "vp", "vice president", "director", "head of", "founder")

JOB_TITLE_POINTS = 20
COMPANY_PRESENT_POINTS = 10
MESSAGE_INTENT_KEYWORDS = ("pricing", "demo", "quote", "buy", "purchase", "trial", "upgrade")
MESSAGE_INTENT_POINTS = 15


def score_lead(lead: Lead) -> tuple[int, list[str]]:
    """Return (score, reasons) so the score is always explainable."""
    score = 0
    reasons: list[str] = []

    source_points = SOURCE_SCORES.get(lead.source, SOURCE_SCORES["unknown"])
    score += source_points
    reasons.append(f"source '{lead.source}': +{source_points}")

    if lead.job_title and any(kw in lead.job_title.lower() for kw in SENIOR_TITLE_KEYWORDS):
        score += JOB_TITLE_POINTS
        reasons.append(f"senior job title '{lead.job_title}': +{JOB_TITLE_POINTS}")

    if lead.company:
        score += COMPANY_PRESENT_POINTS
        reasons.append(f"company provided: +{COMPANY_PRESENT_POINTS}")

    if lead.message and any(kw in lead.message.lower() for kw in MESSAGE_INTENT_KEYWORDS):
        score += MESSAGE_INTENT_POINTS
        reasons.append(f"high-intent language in message: +{MESSAGE_INTENT_POINTS}")

    return score, reasons
