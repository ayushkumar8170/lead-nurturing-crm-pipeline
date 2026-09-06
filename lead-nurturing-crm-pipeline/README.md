# Automated Lead Nurturing & CRM Routing Pipeline

An automated pipeline that takes inbound marketing leads (from a form, ad platform,
or landing page webhook), standardizes and de-duplicates them, scores intent, routes
them to the correct CRM stage, kicks off the right email nurture sequence, and pings
the right sales rep — all with no manual triage.

Originally built as a **Make.com (Integromat)** scenario with multi-branch routing
logic. This repo contains a Python-native equivalent of that pipeline (a Flask
webhook service) plus documentation of the Make.com scenario architecture, so the
logic is portable, testable, and reviewable as real source code.

## What it does

```
 Inbound Webhook (form fill / ad lead / landing page)
     │
     ▼
┌──────────────────────────┐
│ 1. Parse & Standardize    │  normalize field names/casing, validate required fields
└─────────┬─────────────────┘
          ▼
┌──────────────────────────┐
│ 2. De-duplication         │  match against existing leads by email/phone fingerprint
└─────────┬─────────────────┘
          ▼
┌──────────────────────────┐
│ 3. Intent Scoring         │  rule-based score from source, engagement, firmographics
└─────────┬─────────────────┘
          ▼
     ┌────┴────┬─────────────┐
     ▼          ▼             ▼
 Hot Lead   Warm Lead     Cold Lead
     │          │             │
     ▼          ▼             ▼
┌──────────────────────────────────┐
│ 4. Branch Logic                   │
│  - Hot  -> notify sales rep now   │
│  - Warm -> enroll nurture seq. B  │
│  - Cold -> enroll nurture seq. A  │
└─────────┬──────────────────────────┘
          ▼
┌──────────────────────────┐
│ 5. CRM Routing            │  push lead + stage to CRM (HubSpot-shaped API)
└──────────────────────────┘
```

## Why this architecture

- **Rule-based intent scoring** (not a black-box model) so sales/marketing can see
  and adjust exactly why a lead was scored hot/warm/cold — important for a system
  that directly interrupts sales reps.
- **De-duplication by fingerprint** (normalized email + phone hash) runs before
  scoring and CRM routing, so the same lead re-submitting a form doesn't create a
  duplicate CRM record or double-enroll in a nurture sequence.
- **Branch logic as explicit, testable functions** (`src/router.py`) rather than
  buried inside no-code filter conditions — the same logic that runs in Make.com's
  filters is unit-testable here.
- **Make.com** (documented in `make_com/`) is the production orchestration/webhook
  layer — `src/pipeline.py`'s Flask app is a Python-native equivalent that doesn't
  require a Make.com account to run, test, or review.

## Repo structure

```
lead-nurturing-crm-pipeline/
├── src/
│   ├── config.py            # env/config loading
│   ├── lead_parser.py       # standardizes inbound JSON payloads
│   ├── dedup_store.py       # SQLite-backed duplicate detection
│   ├── intent_scorer.py     # rule-based lead intent scoring
│   ├── router.py            # branch logic: hot / warm / cold
│   ├── nurture_sequencer.py # triggers email nurture sequences
│   ├── crm_client.py        # pushes lead + stage to CRM
│   ├── notifier.py          # Slack/email alert to sales reps
│   └── pipeline.py          # Flask app: webhook entrypoint wiring it together
├── make_com/
│   └── scenario_blueprint.md
├── tests/
│   ├── test_lead_parser.py
│   ├── test_dedup_store.py
│   └── test_intent_scorer.py
├── examples/
│   └── sample_lead_payload.json
├── data/                     # local sqlite db lives here (gitignored)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

```bash
git clone <your-repo-url>
cd lead-nurturing-crm-pipeline
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
```

Required environment variables:

| Var                  | Purpose                                             |
|-----------------------|------------------------------------------------------|
| `CRM_API_BASE_URL`    | Base URL of your CRM's REST API                      |
| `CRM_API_KEY`         | CRM auth token                                       |
| `EMAIL_API_KEY`       | Email service provider key (SendGrid-shaped)         |
| `SLACK_WEBHOOK_URL`   | Slack incoming webhook for sales-rep notifications    |
| `HOT_LEAD_THRESHOLD`  | Score cutoff for "hot" (default: 75)                 |
| `WARM_LEAD_THRESHOLD` | Score cutoff for "warm" (default: 40)                |

## Running it

```bash
python -m src.pipeline
# Flask app listening on :5000, endpoint: POST /webhook/lead
```

Send a test lead:

```bash
curl -X POST http://localhost:5000/webhook/lead \
  -H "Content-Type: application/json" \
  -d @examples/sample_lead_payload.json
```

This will parse and standardize the payload, check for duplicates, score intent,
route it (hot/warm/cold), trigger the matching nurture sequence or sales
notification, and push the lead to the CRM with its resolved stage.

## Tests

```bash
pytest tests/
```

## Make.com scenario

The production scenario runs as a Make.com webhook-triggered flow with a Router
module implementing the hot/warm/cold branches. See
[`make_com/scenario_blueprint.md`](make_com/scenario_blueprint.md) for the
module-by-module breakdown — Make.com scenarios export as platform-proprietary
JSON, so this doc is the reviewable reference instead.

## Results

- Eliminated duplicate lead records across the funnel via fingerprint-based dedup.
- Cut sales response time on high-intent leads by routing hot leads to instant
  rep notification instead of a daily CRM review.
- Standardized inconsistent field formats (phone numbers, casing, source labels)
  from multiple lead-gen sources into one CRM schema.

## License

MIT — see [LICENSE](LICENSE).
