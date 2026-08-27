# Local setup guide

## Required tools

Install these once:

1. **Python 3.11+** — runs the FastAPI server and tests.
2. **pip and venv** — installs project packages in an isolated environment.
3. **Git** — version control and collaboration.
4. **A modern browser** — test Chrome, Firefox, Safari, and Edge if possible.
5. **A code editor** — VS Code is a convenient option, but any editor works.

Optional but recommended for the next phase:

- Node.js 20+ and Playwright for automated cross-browser/mobile smoke tests.
- Lighthouse or axe DevTools for performance and accessibility checks.
- A network throttling tool or browser DevTools to test slow 3G and offline recovery.

## Linux (Debian / Ubuntu)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

## macOS

Install Python and Git with Homebrew if they are not already available:

```bash
brew install python git
```

## Windows

Install Python from python.org and tick **Add Python to PATH** during setup. Install Git from git-scm.com. Use PowerShell for the commands below.

## Project install and run

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate            # macOS/Linux
# .venv\Scripts\Activate.ps1        # Windows PowerShell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` and use `DEMO-7824`. Do not enter a real ration card number, Aadhaar number, OTP, phone number, or payment detail into this prototype.

## Checks before a demo

```bash
python -m pytest -q
python -m compileall app.py
```

Then manually test:

- English, Hindi, and Tamil switching.
- Entitlement lookup with `DEMO-7824` and an unknown reference.
- Shop search for Chennai and Pune.
- Complaint submission and ticket tracking.
- Keyboard-only navigation and high contrast mode.
- Mobile width around 360–390px.
- DevTools offline mode and slow 3G throttling.

## Suggested team split

- **Teammate A — citizen experience:** copy, translations, responsive UI, accessibility, journey testing, demo video.
- **Teammate B — service reliability:** API contracts, state-adapter abstraction, caching/error states, tests, deployment, architecture slide.

Both teammates should review the final flow together with someone who is not familiar with the implementation.
