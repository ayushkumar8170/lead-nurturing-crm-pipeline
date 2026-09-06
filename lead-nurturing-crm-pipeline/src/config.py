"""
Centralized configuration loading for the lead nurturing pipeline.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    crm_api_base_url: str
    crm_api_key: str
    email_api_key: str
    slack_webhook_url: str
    hot_lead_threshold: int = 75
    warm_lead_threshold: int = 40
    db_path: str = "data/leads.db"

    def validate(self) -> None:
        missing = [
            name
            for name, value in (
                ("CRM_API_BASE_URL", self.crm_api_base_url),
                ("CRM_API_KEY", self.crm_api_key),
                ("EMAIL_API_KEY", self.email_api_key),
                ("SLACK_WEBHOOK_URL", self.slack_webhook_url),
            )
            if not value
        ]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variable(s): {', '.join(missing)}. "
                "Copy .env.example to .env and fill in your values."
            )


def load_settings() -> Settings:
    return Settings(
        crm_api_base_url=os.getenv("CRM_API_BASE_URL", ""),
        crm_api_key=os.getenv("CRM_API_KEY", ""),
        email_api_key=os.getenv("EMAIL_API_KEY", ""),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        hot_lead_threshold=int(os.getenv("HOT_LEAD_THRESHOLD", "75")),
        warm_lead_threshold=int(os.getenv("WARM_LEAD_THRESHOLD", "40")),
        db_path=os.getenv("DB_PATH", "data/leads.db"),
    )
