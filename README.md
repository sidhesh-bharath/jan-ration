# JanRation

JanRation is a user-focused, multilingual PDS portal concept with a separate developer surface for Fair Price Shop and POS integrations. It is a non-official prototype: every profile, OTP, shop, map position, transaction, and complaint is synthetic.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`. The cardholder flow uses `DEMO-7824`; the dummy OTP is `246810`. The developer portal is at `/developers`, and FastAPI’s interactive OpenAPI reference is at `/docs`.

Run the automated API checks:

```bash
pytest -q
```

## What is implemented

- Consumer-first homepage with an explicit five-step cardholder journey.
- Dummy OTP authentication before the ration dashboard can be opened.
- Allocation bars showing total, withdrawn, and remaining Rice, Wheat, Toor dal, and Sugar.
- Five-state synthetic shop directory with a responsive illustrative map, selectable markers, stock, queue, hours, accessibility, and ONORC signals.
- Dedicated complaints section with pre-populated tickets, statuses, updates, and a new-ticket form.
- English, Hindi, Tamil, Marathi, Bengali, Telugu, Kannada, and Malayalam language options.
- High-contrast mode, system-only fonts, reduced-motion support, focus-visible states, keyboard-friendly controls, and no external font dependency.
- Short-lived demo session state, clear data disclosures, offline fallbacks, and fixed-size loading states to avoid button flicker or layout shifts.
- Developer portal showing the API contract, POS/shop-to-state-adapter architecture, India Stack-aligned intent, safety principles, and a link to interactive OpenAPI docs.
- Favicon containing `ज`.

## API surface

- `POST /api/auth/request-otp`
- `POST /api/auth/verify-otp`
- `GET /api/dashboard` — requires the demo session token.
- `GET /api/shops`
- `POST /api/transactions` — synthetic POS lift event with idempotency.
- `POST /api/webhooks/stock` — synthetic stock update with idempotency.
- `GET /api/complaints`
- `POST /api/complaints`
- `GET /api/portability`
- `GET /api/states`
- `GET /api/health`

The real production version should place state adapters, identity/consent, idempotency, audit logging, rate limits, circuit breakers, and queues behind these stable contracts. Do not connect real citizen data to this prototype.

## Deployment

The repository includes a Vercel entrypoint (`api/index.py`) and `vercel.json`. The same FastAPI service keeps the static portal, developer portal, mock API, and health check together.

To clear synthetic complaints, updates, and test event logs on a running deployment:

```bash
curl --request POST https://janration.vercel.app/api/demo/reset \
  --header 'X-Demo-Reset-Token: demo-reset-token'
```

Set `JANRATION_DEMO_RESET_TOKEN` in deployment settings before sharing a public URL.
