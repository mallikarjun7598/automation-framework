# Mini Retail — End-to-End Web + Mobile Automation Framework

A small, easy-to-follow project that demonstrates the **complete lifecycle** of an
application: **develop → test (web + mobile) → run through a CI/CD pipeline**.

The app under test is a deliberately tiny Amazon-retail-style storefront, so you
can focus on the automation and pipeline mechanics rather than business logic.

---

## What's inside

| Layer | Technology | Why |
|-------|-----------|-----|
| **App (development)** | Flask (Python) | Tiny storefront: browse, search, cart, checkout |
| **Web automation** | Playwright + pytest | Modern, fast, readable browser automation |
| **Mobile automation** | Appium + Selenium + pytest | Industry standard for mobile; drives the same site in a mobile browser |
| **Reporting** | pytest-html | Self-contained HTML test reports |
| **Quality** | ruff | Lint + format |
| **Local CI** | `ci/run-ci.sh` + `Makefile` | Run the whole pipeline on your machine |
| **Hosted CI/CD** | GitHub Actions | Real-world pipeline reference |

The web and mobile suites **share the same selectors** (`data-testid` hooks in the
HTML), so you can see how one app is validated across two very different drivers.

---

## Project structure

```
automation-framework/
├── app/                        # ── DEVELOPMENT: the app under test ──
│   ├── server.py               #    Flask app factory + routes
│   ├── templates/              #    HTML pages (with data-testid hooks)
│   └── static/style.css
│
├── tests/                      # ── TESTING ──
│   ├── web/                    #    Playwright suite
│   │   ├── conftest.py         #    auto-starts the app, provides base_url
│   │   ├── pages/              #    Page Objects (base, home, cart, checkout)
│   │   └── test_shopping_web.py
│   └── mobile/                 #    Appium suite (mobile-web)
│       ├── conftest.py         #    Appium driver fixture (skips w/o device)
│       ├── pages/              #    Mobile Page Objects
│       └── test_shopping_mobile.py
│
├── ci/run-ci.sh                # ── CI/CD: local pipeline mock-up ──
├── .github/workflows/ci.yml    #    hosted pipeline (GitHub Actions)
├── .pre-commit-config.yaml     #    pre-commit hooks
├── Makefile                    #    convenience targets
├── pytest.ini                  #    test config + markers
├── requirements.txt
└── reports/                    #    generated HTML reports
```

---

## Quick start

Prerequisites: **Python 3.12** and (for the web browser) nothing else — Playwright
downloads its own browser. On macOS with Homebrew: `brew install python@3.12`.

```bash
cd automation-framework

# 1. Install everything (venv + deps + Chromium)
make install

# 2. Run the app and open it in your browser (optional, to see it)
make app
#    → http://127.0.0.1:5001

# 3. Run the web tests (auto-starts the app)
make test-web

# 4. Run the full local CI pipeline
make ci
```

Run `make help` to list all targets.

---

## The development → testing → CI/CD workflow

### 1. Development
Edit the app in `app/`. The storefront supports browsing, `?q=` search, a
session cart, and checkout. Every element automation needs has a stable
`data-testid` attribute, e.g. `data-testid="add-to-cart"`. The `/health`
endpoint lets the pipeline confirm the app is up.

### 2. Testing

**Web (runs now):**
```bash
make test-web
```
The suite starts the Flask app on a free port, drives Chromium through the
shopping journey, and writes `reports/web-report.html`.

**Mobile (scaffold — skips until a device is available):**
```bash
make test-mobile          # skips cleanly without Appium/device
make test-mobile-real     # runs for real (needs Appium + emulator/simulator)
```
The mobile suite automates the **same** storefront inside a mobile browser
(Safari on iOS Simulator / Chrome on Android emulator). Tests **skip** rather
than fail when no device is present, so the pipeline stays green everywhere.

To run mobile tests for real:
```bash
npm install -g appium
appium driver install xcuitest       # iOS  (needs Xcode + Simulator)
#   or
appium driver install uiautomator2   # Android (needs Android SDK + emulator)
appium                               # start the server (port 4723)

# in another terminal:
PORT=5001 make app                   # start the app
make test-mobile-real
```

### 3. CI/CD

**Local pipeline mock-up:**
```bash
make ci            # ./ci/run-ci.sh
```
Runs the six stages below in order and stops on the first failure.

**Hosted pipeline:** `.github/workflows/ci.yml` runs the same stages on GitHub
Actions on every push/PR, uploads the HTML reports as artifacts, and includes a
mock deploy step that only runs on `main` after tests pass.

---

## Pipeline diagram

```
          ┌─────────────┐
  commit  │   SETUP     │  create venv, install deps
  ───────▶│  (stage 1)  │
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │    LINT     │  ruff static analysis
          │  (stage 2)  │
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │ BUILD/BOOT  │  start app, poll /health
          │  (stage 3)  │
          └──────┬──────┘
                 ▼
        ┌────────┴────────┐
        ▼                 ▼
 ┌─────────────┐   ┌─────────────┐
 │  WEB TESTS  │   │ MOBILE TESTS│   run in parallel on hosted CI
 │  Playwright │   │   Appium    │   (sequential locally)
 │  (stage 4)  │   │  (stage 5)  │
 └──────┬──────┘   └──────┬──────┘
        └────────┬────────┘
                 ▼
          ┌─────────────┐
          │   REPORT    │  HTML reports (artifacts in CI)
          │  (stage 6)  │
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │   DEPLOY    │  main branch only, after tests pass
          │   (mock)    │
          └─────────────┘
```

---

## Running specific test subsets

```bash
# by marker
.venv/bin/python -m pytest -m web          # web only
.venv/bin/python -m pytest -m mobile       # mobile only
.venv/bin/python -m pytest -m "not mobile" # everything except mobile

# headed (watch the browser) for debugging web tests
.venv/bin/python -m pytest tests/web -m web --browser chromium --headed

# single test
.venv/bin/python -m pytest tests/web/test_shopping_web.py::test_full_checkout_journey
```

---

## Pre-commit hooks (optional)

```bash
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install
```
Now `git commit` runs ruff lint + format and basic file checks on changed files.

---

## Design notes & conventions

- **Page Object Model.** Selectors live in `pages/`, not in tests. If the markup
  changes, you update one place. Tests read as user intent.
- **`data-testid` selectors.** Decoupled from styling/text, so refactors and copy
  changes don't break tests.
- **Self-contained suites.** The web suite starts/stops its own app. Point it at an
  already-running instance by setting `BASE_URL`.
- **Graceful mobile skips.** The mobile suite never fails for lack of a device — it
  skips, so the same pipeline is green on a laptop and runnable on a device farm.
- **Pinned dependencies.** `requirements.txt` pins versions for reproducible builds.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `make install` fails building wheels | Ensure you're on Python 3.12 (`python3.12 --version`). Newer versions may lack prebuilt wheels. |
| Web tests can't find the browser | Run `.venv/bin/python -m playwright install chromium`. |
| Port 5001 already in use | Stop the stray process, or set `PORT` to another value. |
| Mobile tests skip | Expected without a device. Pass `--appium` with Appium + an emulator running. |
