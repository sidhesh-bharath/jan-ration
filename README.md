# JanRation

JanRation is a responsive, multilingual hackathon prototype for a simpler public distribution system (PDS) experience across India.

## Run locally

Requirements: Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. Use the synthetic card reference `DEMO-7824` to view the demo entitlement.

Run the API tests with:

```bash
pytest -q
```

## What is included

- Responsive citizen-first landing page
- Four core tasks: entitlement, shop discovery, request tracking, and grievance reporting
- Synthetic FastAPI endpoints with clear demo-mode behavior
- English, Hindi, and Tamil UI switching
- High-contrast mode, keyboard-friendly controls, skip link, readable error states, and browser speech for the entitlement answer
- No external fonts, images, analytics, government logos, or live PDS calls

Read [PROJECT_PLAN.md](PROJECT_PLAN.md) for the product thesis, portal analysis, architecture, roadmap, reliability plan, safety boundaries, and hackathon demo strategy.

## Next engineering step

Add Playwright smoke tests for the main mobile and desktop journeys, then extract the front-end copy into versioned translation files reviewed by native speakers. Only after that should you implement state adapters behind the existing API contract.
