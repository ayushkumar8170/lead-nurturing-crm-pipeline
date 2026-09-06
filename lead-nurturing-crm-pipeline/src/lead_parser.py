"""
Parses and standardizes inbound lead JSON payloads.

Different lead sources (form builders, ad platforms, landing page tools) send
wildly inconsistent field names and formats. This module normalizes them into
one canonical `Lead` shape before anything downstream touches the data.
"""

import re
from dataclasses import dataclass, field
from typing import Any

# Maps known variant field names (lowercased) to our canonical field name.
FIELD_ALIASES = {
    "email": "email",
    "e-mail": "email",
    "email_address": "email",
    "full_name": "name",
    "fullname": "name",
    "name": "name",
    "first_name": "first_name",
    "last_name": "last_name",
    "phone": "phone",
    "phone_number": "phone",
    "mobile": "phone",
    "company": "company",
    "company_name": "company",
    "organization": "company",
    "source": "source",
    "utm_source": "source",
    "lead_source": "source",
    "message": "message",
    "comments": "message",
    "job_title": "job_title",
    "title": "job_title",
}


class LeadValidationError(ValueError):
    """Raised when a required field is missing or invalid."""


@dataclass
class Lead:
    email: str
    name: str = ""
    phone: str = ""
    company: str = ""
    source: str = "unknown"
    job_title: str = ""
    message: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        """Stable identity for de-duplication: normalized email, or phone if no email."""
        if self.email:
            return f"email:{self.email.strip().lower()}"
        digits = re.sub(r"\D", "", self.phone)
        return f"phone:{digits}"


def _normalize_phone(raw_phone: str) -> str:
    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}" if digits else ""


def parse_lead(payload: dict[str, Any]) -> Lead:
    """Standardize an arbitrary inbound payload into a canonical Lead."""
    normalized: dict[str, Any] = {}

    for raw_key, value in payload.items():
        key = FIELD_ALIASES.get(raw_key.strip().lower().replace(" ", "_"))
        if key and value not in (None, ""):
            normalized[key] = str(value).strip()

    email = normalized.get("email", "").lower()
    phone = _normalize_phone(normalized.get("phone", ""))

    if not email and not phone:
        raise LeadValidationError(
            "Lead payload must include at least an email or a phone number."
        )

    name = normalized.get("name", "")
    if not name and (normalized.get("first_name") or normalized.get("last_name")):
        name = f"{normalized.get('first_name', '')} {normalized.get('last_name', '')}".strip()

    return Lead(
        email=email,
        name=name,
        phone=phone,
        company=normalized.get("company", ""),
        source=normalized.get("source", "unknown").lower(),
        job_title=normalized.get("job_title", ""),
        message=normalized.get("message", ""),
        raw=payload,
    )
