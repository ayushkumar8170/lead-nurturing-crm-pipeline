import pytest

from src.lead_parser import LeadValidationError, parse_lead


def test_parses_varied_field_names():
    payload = {
        "Full Name": "Jordan Ellis",
        "Email Address": "Jordan.Ellis@Example.com",
        "Phone Number": "(555) 123-4567",
        "Company Name": "Ellis & Co",
        "UTM Source": "demo_request",
    }
    lead = parse_lead(payload)

    assert lead.email == "jordan.ellis@example.com"
    assert lead.name == "Jordan Ellis"
    assert lead.phone == "+15551234567"
    assert lead.company == "Ellis & Co"
    assert lead.source == "demo_request"


def test_builds_name_from_first_last_when_missing():
    payload = {"email": "a@b.com", "first_name": "Ada", "last_name": "Lovelace"}
    lead = parse_lead(payload)
    assert lead.name == "Ada Lovelace"


def test_raises_when_no_email_or_phone():
    with pytest.raises(LeadValidationError):
        parse_lead({"name": "No Contact Info"})


def test_fingerprint_prefers_email():
    lead = parse_lead({"email": "a@b.com", "phone": "5551234567"})
    assert lead.fingerprint == "email:a@b.com"


def test_fingerprint_falls_back_to_phone():
    lead = parse_lead({"phone": "555-123-4567"})
    assert lead.fingerprint == "phone:5551234567"
