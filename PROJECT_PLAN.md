# JanRation project plan

## 1. Product thesis

JanRation is a non-official concept for a single, citizen-first front door to India’s Public Distribution System (PDS). It does not replace state systems. It translates them into one predictable experience, then routes the request to the correct state adapter.

The primary problem is not that citizens lack a PDS website. It is that the journey is fragmented: a person has to know which state portal owns which task, understand government terms, tolerate inconsistent layouts, and recover when a service or device is unavailable. The winning demo should make one important journey feel dramatically easier: **“I need to know what I can collect, where I can collect it, and what to do if I don’t receive it.”**

## 2. What the current portals reveal

Reference portals expose useful capabilities, but the citizen experience is split across them:

- TNPDS, MahaFood, and AePDS/J&K represent separate state or state-linked entry points with different navigation, terminology, and service locations.
- MahaFood lists common operations such as a new ration card, member/name/address changes, duplicate card copies, and Fair Price Shop registration, but these are linked out to another system. That creates context switching and makes it hard to know what happens next.
- The J&K AePDS landing page is JavaScript-dependent in a basic fetch, which is a warning sign for low-end devices, older browsers, assistive technology, or a user on an unstable connection.
- Official PDS guidance confirms the need for entitlement visibility, nearby FPS discovery, transaction history, Aadhaar-seeding status, portability/ONORC guidance, feedback, and grievance support.
- The system is inherently federated: state-specific eligibility and workflows must remain authoritative, while the shared layer should standardize language, status, accessibility, caching, analytics, and error recovery.

## 3. MVP for the hackathon

The prototype in this repository demonstrates a complete, synthetic citizen flow:

1. Land on a calm, responsive home screen with four plain-language tasks.
2. Choose “See my ration” and enter the safe demo reference `DEMO-7824`.
3. Receive a readable entitlement summary for rice, wheat, and dal, including the next collection window.
4. Continue to “Find my shop” and view nearby synthetic Fair Price Shops with opening hours, distance, reference, and reported stock note.
5. Use “Report a problem” to submit a synthetic complaint and receive a trackable ticket reference.
6. Open “Track a request” to see the proposed plain-language status pattern.

The UI also includes English, Hindi, and Tamil switching, browser speech for the entitlement answer where supported, a high-contrast toggle, keyboard-friendly controls, a skip link, mobile layouts, and visible prototype-data disclosure.

## 4. Recommended product scope after the demo

### Citizen services

- “What can I collect?”: entitlement by month, household member, commodity, price, and last refresh time.
- “Where can I collect?”: location-aware FPS map/list, open now, accessibility, queue estimate, stock freshness, directions, and portability eligibility.
- “My family”: add/remove member, address change, card correction, duplicate card, and downloadable e-ration card where the state supports it.
- “My history”: recent transactions, partial lifts, failed authentication, and an explanation of each status.
- “Get help”: guided complaint builder, evidence upload only with explicit consent, ticket timeline, escalation deadline, call-back preference, and assisted-service mode.
- “Am I eligible?”: a decision tree in simple language with a document checklist and state-specific handoff.
- Migrant mode: choose home state and current location, understand ONORC portability, find a nearby enabled shop, and see what happens if only part of the entitlement is collected.

### Inclusion and accessibility

- Default language based on browser/device, always changeable.
- Human-reviewed translations for every supported state language; never rely on raw machine translation for legal or entitlement text.
- Read-aloud for key answers, large tap targets, high contrast, reduced motion, clear focus order, screen-reader labels, and text alternatives for maps.
- Assisted mode for CSC/volunteer/family help: short-lived session, explicit consent, masked identifiers, and an activity receipt.
- Low-bandwidth mode: no mandatory map tiles, compressed assets, cached last-known answers, retry queues, and a visible “last updated” timestamp.
- IVR/USSD/SMS handoff for citizens who cannot use a smartphone.

### Trust and safety

- Never ask JanRation to store Aadhaar, OTP, payment, or biometric data in the shared layer.
- Use state-owned identity and consent boundaries; exchange only the minimum tokenized reference needed for a request.
- Every answer shows source, timestamp, confidence/availability, and what is mock versus live.
- Government logos and language that imply endorsement are intentionally excluded.
- Audit trails, rate limits, encryption, retention limits, threat modeling, and an incident playbook belong in the production design.

## 5. Architecture and tech stack

### Hackathon build

- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic. FastAPI provides typed, testable endpoints and an OpenAPI contract without slowing the team down.
- **Frontend:** semantic HTML, modern CSS, and dependency-light JavaScript. The first prototype avoids a large client framework and external fonts so it loads reliably and can be understood by both teammates.
- **Data:** synthetic in-memory records now. Use PostgreSQL for service metadata, Redis for short-lived caches/rate limits, and object storage for consented documents later.
- **Testing:** pytest + FastAPI TestClient now; Playwright for cross-browser journeys next.
- **Deployment:** containerized FastAPI behind a CDN/reverse proxy, health checks, autoscaling, regional redundancy, and an adapter-worker queue for slow state dependencies.

### Production-scale shape

`Citizen UI → API gateway → shared PDS experience API → state adapters → state PDS systems`

Cross-cutting services: translation/content service, consent and identity broker, cache/read model, observability, notifications, grievance workflow, and feature flags. Each state adapter should have a contract test suite and a circuit breaker. If an adapter fails, the shared layer should return a stale-but-labeled read view or a clear next action rather than a blank error page.

## 6. 48-hour hackathon execution plan

### Phase A — sharpen the story (2–3 hours)

- Interview two people who have used a ration shop or helped a family member.
- Pick one hero scenario: a migrant worker checking entitlement and finding a shop in a new city.
- Write a before/after script and define three success metrics: time to first useful answer, task completion rate, and comprehension of next action.

### Phase B — build the citizen journey (8–12 hours)

- Build the home screen, entitlement lookup, shop finder, complaint ticket, and tracking state.
- Add mobile breakpoints, keyboard navigation, language switch, empty/loading/error states, and last-updated labels.
- Keep all personal data synthetic and show the disclosure on-screen.

### Phase C — reliability and inclusion pass (4–6 hours)

- Test throttled 3G, offline/reconnect, small screens, keyboard only, Chrome/Firefox/Safari/Edge, and a screen reader.
- Add a “service unavailable” state that offers a cached answer or a phone/assisted-service next step.
- Run automated API tests and a browser smoke test.

### Phase D — submission polish (4–6 hours)

- Record a two-minute demo: first minute as a citizen, second minute on architecture and why it scales.
- Keep a visible “what is mocked” list.
- Deploy to a public URL with no login requirement; include demo reference in the landing screen.
- Prepare the under-250-word summary around one problem, one journey, and measurable improvement.

## 7. Suggested judging metrics

- A first-time user reaches their entitlement in under 60 seconds.
- A user can say what to collect, where to go, and what to do next after one screen.
- The same core task works at 360px width and with a keyboard.
- A dependency outage produces a useful recovery state rather than a generic error.
- Translation coverage and terminology are reviewed by native speakers, not just machine output.

## 8. Risks and honest limits

This repository is a prototype. It does not connect to live government systems, authenticate a real person, validate eligibility, use Aadhaar, issue a ration card, or guarantee stock. The synthetic data and mock endpoints are deliberate and align with the hackathon brief’s safety requirements. State integration, legal review, operational ownership, translation QA, security review, and public procurement/adoption are separate phases.
