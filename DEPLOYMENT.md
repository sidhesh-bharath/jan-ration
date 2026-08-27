# JanRation deployment

## Recommended hackathon path: Render

Render is a good fit for this monolithic prototype because one public web service can serve the consumer portal, `/developers`, FastAPI `/docs`, and the synthetic API under the same origin. That avoids CORS and split-host surprises during judging.

### Deploy from GitHub

1. Create a GitHub repository and push this project.
2. Create a new **Web Service** in Render and select the repository.
3. Choose the Python runtime.
4. Use these commands if Render does not detect `render.yaml`:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Set the health check path to `/api/health`.
6. Deploy and open the generated HTTPS URL.
7. Test these public URLs before sharing:
   - `/` — cardholder portal
   - `/developers` — developer portal
   - `/docs` — interactive API reference
   - `/api/health` — deployment health check
8. Record the demo instructions somewhere visible: `DEMO-7824`, dummy OTP `246810`, and “synthetic data only”.

The included `render.yaml` can be used as a Blueprint configuration. The `Dockerfile` is an alternative if the team prefers an explicit container build.

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
