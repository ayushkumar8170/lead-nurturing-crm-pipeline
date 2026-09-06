# Make.com Scenario Blueprint

Make.com scenarios are stored as platform-proprietary JSON tied to your account's
connections (API keys, webhook IDs), so they aren't portable or reviewable as
plain source code. This document is the reference for rebuilding the production
scenario module-by-module, and maps 1:1 to the Python modules in `src/`.

## Trigger

**Module:** Webhooks — Custom webhook
Receives the raw inbound JSON payload from whichever lead source fired it
(landing page form, ad platform lead form, chatbot, etc). Each source is
pointed at the same webhook URL.

## Module 1 — Parse & standardize

**Module:** JSON — Parse JSON, then a series of **Set variable** modules
Maps each known source's field names onto a canonical set of variables
(`email`, `name`, `phone`, `company`, `source`, `job_title`, `message`) —
equivalent to `src/lead_parser.py`'s `FIELD_ALIASES` table.

## Module 2 — De-duplication

**Module:** Data Store — Get a record (keyed by normalized email/phone)
- **Filter:** if a record already exists for this fingerprint, route to an
  end-of-scenario "duplicate, do nothing" path.
- If not found: **Data Store — Add a record** to mark it seen, then continue.

## Module 3 — Intent scoring

**Module:** Set multiple variables, using Make.com's numeric/text functions to
replicate the rule table in `src/intent_scorer.py` (source points + seniority
keyword match + company-present + message-intent keywords), summed into a
single `lead_score` variable.

## Module 4 — Router (branch logic)

**Module:** Router, with three branches gated by **Filter** conditions on
`lead_score`:
- `lead_score >= 75` → Hot branch
- `40 <= lead_score < 75` → Warm branch
- `lead_score < 40` → Cold branch

### Hot branch
**Module:** Slack — Create a message, posted to the sales team's channel with
lead details and the scoring breakdown.

### Warm / Cold branches
**Module:** HTTP — Make a request to the email platform's API to enroll the
contact in the corresponding nurture sequence/list ID.

## Module 5 — CRM routing

**Module:** HTTP — Make a request (or the native CRM app if installed, e.g.
HubSpot — Create/Update a Contact)
- Upserts the contact with all standardized fields, the resolved
  `pipeline_stage`, and the numeric `lead_score`.

## Error handling

Each HTTP/API module has a fallback route (Make.com's built-in error handler)
that posts a Slack message to `#pipeline-alerts` on failure, so a bad API
response or malformed payload doesn't fail silently and lose a lead.

## Porting notes

If rebuilding this on Zapier, n8n, or a custom serverless handler, the module
order above is exactly what `src/pipeline.py`'s `process_lead()` does in
code — use it as the reference implementation for request bodies, scoring
rules, and branch thresholds.
