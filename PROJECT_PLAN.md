# JanRation product and engineering plan

## Product position

JanRation is a citizen-first front door to India’s Public Distribution System. It is not an official government portal and it does not replace state ownership. The cardholder sees one calm experience; state-specific rules and source systems stay behind independently tested adapters.

The hero problem is simple: a person should be able to answer three questions without portal-hopping:

1. What can my household collect this month?
2. Where can I collect it, and is that shop suitable today?
3. What can I do if the quantity, shop, authentication, or service is wrong?

## What changed in this overhaul

The previous UI read like a pitch deck. The new structure reads like a public service:

- Consumer language, household journey, and next actions lead the home page.
- The ration dashboard is behind a dummy OTP flow, with an evaluator-friendly `DEMO-7824` shortcut and `246810` synthetic OTP.
- Allocation bars show total quota, withdrawn amount, and remaining balance for rice, wheat, dal, and sugar.
- The store locator is a list-plus-map experience: selecting either a card or map marker selects the same store.
- Complaints live in a dedicated support section with synthetic history, status, update text, and a new complaint form.
- The developer portal is a separate `/developers` route and links to FastAPI’s interactive `/docs` and `/openapi.json` resources.
- All eight language choices are present: English, Hindi, Tamil, Marathi, Bengali, Telugu, Kannada, and Malayalam.
- Favicon, metadata, headings, and visible product language are JanRation branded.
- Footer links now lead to sections, the API portal, or meaningful modals. The small “Prototype limitations” link is intentionally discreet but functional.

## User journey

### Cardholder

1. Arrive at JanRation and choose “Check my ration”.
2. Enter a card reference or tap `DEMO-7824`.
3. Receive a synthetic OTP. The demo explains that no SMS was sent.
4. Enter `246810` to open the household view.
5. Scan the allocation bars and recent collection history.
6. Find a suitable shop using state, district, ONORC, stock, hours, queue, and accessibility signals.
7. Select a map marker to see the shop details and inventory snapshot.
8. If needed, open the separate Support section, review previous tickets, and create a new complaint.

### Migrant worker / ONORC

1. Open “If you are away from home”.
2. Select home state and current state.
3. Read the three-step portability guidance and suggested shop reference.
4. Confirm the quantity and price shown on the POS screen before completing a lift.

## Developer portal and API focus

The developer portal explains the shared service layer in terms of the actors that matter:

`FPS / ePoS → JanRation API → state adapter → entitlement / inventory / event ledger`

The contract is intentionally small and predictable:

- `POST /api/auth/request-otp`
- `POST /api/auth/verify-otp`
- `GET /api/dashboard`
- `GET /api/shops`
- `GET /api/complaints`
- `POST /api/complaints`
- `GET /api/portability`
- `GET /api/states`
- `GET /api/health`

The developer page documents and the sandbox exposes synthetic write contracts such as `POST /api/transactions` and `POST /api/webhooks/stock`. Both require the clearly labelled demo shop token and protect retries with an idempotency key. They never update a real ledger.

## India Stack-aligned intent

“Aligned” here means the design follows interoperable public-infrastructure principles; it is not a claim of government certification.

- Consent and purpose before accessing a citizen view.
- Tokenized references and minimum data exchange.
- No retention of Aadhaar, biometrics, OTP delivery data, or payment details in the shared layer.
- Idempotency keys for POS writes so retries cannot double-deduct.
- Human-readable receipts and ticket references.
- Audit logs for who initiated an event and which adapter answered.
- Webhooks/events for inventory and service updates.
- Circuit breakers, queues, and last-known read models for unreliable state dependencies.

## Accessibility and resilience

- System-only font stack: no external font request can fail or cause a flash of unstyled text.
- Semantic headings, labels, landmarks, `focus-visible`, skip navigation, keyboard controls, and live announcements.
- High-contrast mode and reduced-motion support.
- Map is supplementary: every store is also available as a readable list.
- Fixed panel/card minimum heights and busy-state indicators preserve geometry during interactions.
- Buttons do not animate with layout-shifting transforms.
- Dashboard and shop data fall back to labeled synthetic local data when the API is unavailable.
- Every synthetic answer carries source/freshness context in the interface.

## Synthetic data policy

The application uses only self-contained synthetic values: the household, card reference, OTP, balances, transactions, store coordinates, inventory, tickets, and timestamps. Any production integration must be designed and reviewed separately. The live government systems named in the competition brief are never called by this code.

## Suggested hackathon demo

Record a two-minute walkthrough:

1. Open the citizen portal, tap `DEMO-7824`, enter `246810`, and show the allocation bars.
2. Click a store in the map and show stock, queue, accessibility, and ONORC signals.
3. Open Support and show the pre-populated active ticket plus creation of a new ticket.
4. Open `/developers` and explain how a POS event travels through the API and state adapter.
5. End with the limitation modal and explain exactly what is mocked.

This directly answers the judging questions from the supplied image: who is affected, what is hard today, what changed, why this is better, what works now, what remains mocked, and how the system can scale safely.

## Post-hackathon build order

1. Have native speakers review every supported-language string.
2. Add Playwright journeys at 360px, 768px, and desktop widths.
3. Add Lighthouse and axe checks to CI.
4. Define signed adapter contracts and conformance fixtures for each state.
5. Add managed storage, consent/identity, queues, observability, and audit retention controls.
6. Run security, privacy, accessibility, legal, and operational reviews before connecting any real service.
