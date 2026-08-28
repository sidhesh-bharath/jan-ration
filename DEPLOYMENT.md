# JanRation deployment

## Recommended hackathon path: Vercel

Vercel serves the consumer portal, `/developers`, FastAPI `/docs`, and synthetic API through `api/index.py` on one origin. This avoids CORS and free-service spin-down behavior.

### Deploy from GitHub

1. Import the repository into Vercel.
2. Keep the project root at the repository root; `vercel.json` selects the Python entrypoint.
3. Add `JANRATION_DEMO_RESET_TOKEN` as an environment variable.
4. Deploy and open the generated HTTPS URL.
7. Test these public URLs before sharing:
   - `/` — cardholder portal
   - `/developers` — developer portal
   - `/docs` — interactive API reference
   - `/api/health` — deployment health check
   - `/api/shops?state=Tamil%20Nadu` — public synthetic shop directory
8. Record the demo instructions somewhere visible: `DEMO-7824`, dummy OTP `246810`, and “synthetic data only”.

The legacy `render.yaml` and `Dockerfile` remain available for local/container fallback.

## Public launch checklist

- Use a non-official product disclaimer in the page and submission notes.
- Do not add real Aadhaar, OTP, payment, household, or shop data.
- Do not put secrets in the repository or frontend JavaScript.
- Keep the demo token and OTP clearly synthetic and short-lived.
- Verify the public URL in a fresh private browser window.
- Test mobile width, slow 3G, offline reload, and all major journeys.
- Run `pytest -q` before recording the demo.
- Keep `/api/health` simple so the platform can restart unhealthy instances.

## Production path after the hackathon

Keep the static UI and developer docs on a CDN if desired, but place the API behind an authenticated gateway. Add a managed PostgreSQL database, Redis, a queue for state-adapter work, centralized logs/metrics, circuit breakers, an audit trail, and a consent/identity broker. Each state adapter should be independently deployable and contract-tested before it can be marked healthy.

The synthetic app intentionally does not attempt any of these live integrations.
