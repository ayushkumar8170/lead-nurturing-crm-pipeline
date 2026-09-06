from src.intent_scorer import score_lead
from src.lead_parser import parse_lead


def test_high_intent_lead_scores_high():
    lead = parse_lead(
        {
            "email": "vp@bigco.com",
            "company": "BigCo",
            "job_title": "VP of Marketing",
            "source": "demo_request",
            "message": "Can we get a demo and pricing?",
        }
    )
    score, reasons = score_lead(lead)
    assert score >= 75
    assert len(reasons) == 4


def test_low_intent_lead_scores_low():
    lead = parse_lead(
        {
            "email": "someone@example.com",
            "source": "organic_social",
        }
    )
    score, reasons = score_lead(lead)
    assert score < 40


def test_unknown_source_defaults_to_baseline():
    lead = parse_lead({"email": "a@b.com"})
    score, _ = score_lead(lead)
    assert score == 5
