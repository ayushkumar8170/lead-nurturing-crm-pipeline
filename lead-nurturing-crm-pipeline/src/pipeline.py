"""
End-to-end orchestration: inbound webhook -> parse -> dedup -> score ->
route -> nurture/notify -> CRM upsert.

This is the Python-native equivalent of the production Make.com scenario
(see make_com/scenario_blueprint.md). Run as a standalone Flask service, or
import `process_lead` into another service/serverless handler.
"""

import logging

from flask import Flask, jsonify, request

from src.config import Settings, load_settings
from src.crm_client import upsert_lead
from src.dedup_store import is_duplicate, record_lead
from src.intent_scorer import score_lead
from src.lead_parser import LeadValidationError, parse_lead
from src.nurture_sequencer import enroll_in_sequence
from src.notifier import notify_sales_rep
from src.router import classify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lead_pipeline")

app = Flask(__name__)


def process_lead(settings: Settings, payload: dict) -> dict:
    """Run the full pipeline for a single inbound lead payload."""
    lead = parse_lead(payload)

    if is_duplicate(settings.db_path, lead.fingerprint):
        logger.info("Duplicate lead skipped: %s", lead.fingerprint)
        return {"status": "duplicate", "fingerprint": lead.fingerprint}

    score, reasons = score_lead(lead)
    decision = classify(score, settings)

    if decision.notify_sales:
        notify_sales_rep(settings, lead, score, reasons)

    if decision.nurture_sequence:
        enroll_in_sequence(settings, lead, decision.nurture_sequence)

    upsert_lead(settings, lead, decision.stage, score)
    record_lead(settings.db_path, lead.fingerprint, decision.stage.value)

    return {
        "status": "processed",
        "stage": decision.stage.value,
        "score": score,
        "reasons": reasons,
        "notified_sales": decision.notify_sales,
        "nurture_sequence": decision.nurture_sequence,
    }


@app.route("/webhook/lead", methods=["POST"])
def webhook_lead():
    settings = load_settings()
    try:
        settings.validate()
    except EnvironmentError as exc:
        return jsonify({"error": str(exc)}), 500

    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "Request body must be JSON."}), 400

    try:
        result = process_lead(settings, payload)
    except LeadValidationError as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception:
        logger.exception("Unhandled error processing lead")
        return jsonify({"error": "Internal error processing lead."}), 500

    return jsonify(result), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
