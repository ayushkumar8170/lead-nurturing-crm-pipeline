"""
Branch logic: classifies a scored lead into hot / warm / cold and decides
which downstream action(s) to take. Kept as plain functions so the same
logic that lives inside Make.com's Router/Filter modules is unit-testable.
"""

from dataclasses import dataclass
from enum import Enum

from src.config import Settings


class LeadStage(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


@dataclass
class RoutingDecision:
    stage: LeadStage
    notify_sales: bool
    nurture_sequence: str | None


def classify(score: int, settings: Settings) -> RoutingDecision:
    if score >= settings.hot_lead_threshold:
        return RoutingDecision(stage=LeadStage.HOT, notify_sales=True, nurture_sequence=None)

    if score >= settings.warm_lead_threshold:
        return RoutingDecision(
            stage=LeadStage.WARM, notify_sales=False, nurture_sequence="warm_nurture_sequence_b"
        )

    return RoutingDecision(
        stage=LeadStage.COLD, notify_sales=False, nurture_sequence="cold_nurture_sequence_a"
    )
