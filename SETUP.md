# JanRation local setup

## Required tools

- Python 3.11 or newer
- `pip` and `venv`
- Git
- A current Chrome, Firefox, Safari, or Edge browser
- Any editor; VS Code is optional

Useful next-phase tools:

- Node.js 20+ and Playwright for automated desktop/mobile journeys.
- Lighthouse and axe DevTools for performance and accessibility checks.
- Browser DevTools network throttling for slow 3G/offline testing.

## Linux

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

## macOS

```bash
brew install python git
```

## Windows

Install Python from python.org with **Add Python to PATH** enabled, then install Git from git-scm.com. Use PowerShell for the commands below.

## Install and run

From the project directory (the folder that contains `app.py`):

If this checkout was moved from another computer or folder, recreate `.venv` first. Python virtual environments store an absolute interpreter path and the copied environment may still point at the old location.

```bash
python3 -m venv .venv
source .venv/bin/activate                 # macOS/Linux
# .venv\Scripts\Activate.ps1             # Windows PowerShell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` for the cardholder portal. Use the safe demo reference `DEMO-7824`, then enter the dummy OTP `246810`. Open `http://127.0.0.1:8000/developers` for the developer portal and `/docs` for interactive OpenAPI documentation.

## Verification checklist

```bash
python -m compileall app.py tests/test_api.py
pytest -q
```

Manually verify:

- Auth cannot open the ration dashboard without the dummy OTP.
- Demo quick-fill opens the OTP flow with `DEMO-7824` already entered.
- Allocation bars show total, withdrawn, and remaining quantities.
- Map markers and shop cards select the same shop.
- Shop filters work for state, district, and ONORC-only.
- Complaints show existing synthetic tickets and create a new ticket.
- Footer links open a real section, page, or modal.
- Prototype limitations open from the discreet footer link.
- All eight language options remain readable on a 360–390px viewport.
- High contrast, keyboard-only focus, reduced motion, and offline fallback work.

Never enter a real ration card number, Aadhaar number, OTP, phone number, payment detail, or precise location into this prototype.
