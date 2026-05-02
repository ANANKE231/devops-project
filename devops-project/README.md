# ⬡ DevOps Demo App

A full-stack Python/Flask web application demonstrating a complete DevOps pipeline: version control, CI/CD, Infrastructure-as-Code, Blue-Green deployment, rollback, and monitoring.

---

## 📋 Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Workflow Diagram](#workflow-diagram)
4. [Step-by-Step Setup](#step-by-step-setup)
   - [1 · Clone & Branch Strategy](#1--clone--branch-strategy)
   - [2 · IaC: Automated Environment Setup](#2--iac-automated-environment-setup)
   - [3 · Run the App Locally](#3--run-the-app-locally)
   - [4 · CI Pipeline (GitHub Actions)](#4--ci-pipeline-github-actions)
   - [5 · CD: Blue-Green Deployment](#5--cd-blue-green-deployment)
   - [6 · Rollback](#6--rollback)
   - [7 · Monitoring & Health Checks](#7--monitoring--health-checks)
5. [API Reference](#api-reference)
6. [Screenshots](#screenshots)

---

## Tech Stack

| Layer | Tool / Language |
|---|---|
| **Web App** | Python 3.11 · Flask 3.0 |
| **Testing** | pytest 8.2 |
| **Linting** | flake8 7.0 |
| **Version Control** | Git · GitHub |
| **CI/CD** | GitHub Actions |
| **IaC / Automation** | Ansible · Bash |
| **Deployment Strategy** | Blue-Green |
| **Monitoring** | Custom Bash health-check script |
| **Logging** | File-based (`/var/log/devops-demo/`) |

---

## Project Structure

```
devops-project/
├── app/
│   └── app.py                  # Flask application
├── tests/
│   └── test_app.py             # pytest unit tests (8 tests)
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions pipeline
├── ansible/
│   ├── setup.yml               # Ansible playbook (IaC)
│   └── inventory.ini           # Ansible inventory
├── scripts/
│   ├── deploy.sh               # Blue-Green deploy script
│   ├── rollback.sh             # Instant rollback script
│   └── health_check.sh         # Health monitor (cron-ready)
├── setup.sh                    # Single-command bootstrap
├── requirements.txt
└── README.md
```

---

## Workflow Diagram

```
Developer Workstation
        │
        ├─ git push → dev branch
        │       │
        │       ▼
        │   ┌─────────────────────────────────────────┐
        │   │         GitHub Actions CI/CD             │
        │   │                                          │
        │   │  ┌──────────┐  ┌──────────┐             │
        │   │  │  LINT    │→ │  TEST    │             │
        │   │  │ (flake8) │  │ (pytest) │             │
        │   │  └──────────┘  └────┬─────┘             │
        │   │                     │ (main branch only) │
        │   │               ┌─────▼──────┐            │
        │   │               │   DEPLOY   │            │
        │   │               │ (Blue-Green)│           │
        │   │               └─────┬──────┘            │
        │   └─────────────────────┼───────────────────┘
        │                         │
        ▼                         ▼
  Pull Request              Production Host
  Review                         │
                       ┌─────────┴─────────┐
                       │                   │
                  ┌────▼────┐         ┌────▼────┐
                  │  BLUE   │  ←live→ │  GREEN  │
                  │ :5001   │         │  :5002  │
                  └─────────┘         └─────────┘
                       │                   │
                       └────────┬──────────┘
                                │
                         Health Monitor
                     (logs → /var/log/devops-demo/)
```

**Branch strategy:**
- `main` — protected, triggers full CI + CD on push
- `dev`  — development branch, triggers CI (lint + test) only

---

## Step-by-Step Setup

### 1 · Clone & Branch Strategy

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/devops-demo.git
cd devops-demo

# The repo ships with two branches
git branch -a
# * main
#   dev

# Work on dev, merge to main to trigger deployment
git checkout dev
# ... make changes ...
git add .
git commit -m "feat: add new endpoint"
git push origin dev

# Open Pull Request: dev → main  (triggers CI on both branches)
# After merge to main → CI + CD runs automatically
```

---

### 2 · IaC: Automated Environment Setup

You have two options — both are single-command.

#### Option A — Bash (fastest)

```bash
bash setup.sh
```

This will:
1. Verify Python 3 is installed
2. Install all pip dependencies
3. Create `/opt/devops-demo/{blue,green,releases}/` directories
4. Create `/var/log/devops-demo/` log directory
5. Stage app files into both deployment slots
6. Copy and chmod all operational scripts
7. Run the full test suite to verify everything works

**Expected output:**
```
[SETUP] DevOps Demo — Environment Setup
[SETUP] ================================
[SETUP] Python 3.11 detected
[SETUP] Installing Python dependencies...
[SETUP] Creating directory structure...
[SETUP] Staging app files...
[SETUP] Running test suite...
8 passed in 0.24s
[SETUP] All tests passed ✅
[SETUP]
[SETUP] ✅  Setup complete!
[SETUP]    Start app:    APP_ENV=production PORT=5001 python3 app/app.py
[SETUP]    Deploy:       bash scripts/deploy.sh v1.0
[SETUP]    Health check: bash scripts/health_check.sh
[SETUP]    Rollback:     bash scripts/rollback.sh
```

#### Option B — Ansible

```bash
# Requires: pip install ansible
ansible-playbook -i ansible/inventory.ini ansible/setup.yml
```

The Ansible playbook (`ansible/setup.yml`) performs identical steps declaratively, with idempotent tasks for directory creation, file copying, and configuration templating.

**Expected output:**
```
PLAY [Provision DevOps Demo App Environment] ***********************************

TASK [Ensure pip is available] *************************************************
ok: [localhost]

TASK [Install Python dependencies] *********************************************
changed: [localhost]

TASK [Create deployment directories] *******************************************
changed: [localhost] => (item=/opt/devops-demo)
changed: [localhost] => (item=/opt/devops-demo/blue)
changed: [localhost] => (item=/opt/devops-demo/green)
changed: [localhost] => (item=/opt/devops-demo/releases)
changed: [localhost] => (item=/var/log/devops-demo)

TASK [Copy app to blue slot] ***************************************************
changed: [localhost]

TASK [Copy app to green slot] **************************************************
changed: [localhost]

TASK [Write blue slot environment config] **************************************
changed: [localhost]

TASK [Write green slot environment config] *************************************
changed: [localhost]

TASK [Write initial active-slot file (blue is live)] ***************************
changed: [localhost]

TASK [Copy deployment scripts] *************************************************
changed: [localhost] => (item=deploy.sh)
changed: [localhost] => (item=rollback.sh)
changed: [localhost] => (item=health_check.sh)

TASK [Setup complete — print summary] ******************************************
ok: [localhost] => {
    "msg": [
        "✅  Environment ready at /opt/devops-demo",
        "🔵  Blue  slot → port 5001",
        "🟢  Green slot → port 5002",
        "📋  Logs  dir  → /var/log/devops-demo",
        "Run: bash /opt/devops-demo/deploy.sh <version>"
    ]
}

PLAY RECAP *********************************************************************
localhost  : ok=10  changed=9  unreachable=0  failed=0  skipped=0
```

---

### 3 · Run the App Locally

```bash
# Start directly
APP_ENV=production PORT=5000 python3 app/app.py

# Visit http://localhost:5000
# Health check: http://localhost:5000/health
```

The app has:
- **`/`** — Web UI with a live message feed
- **`/health`** — JSON health check endpoint
- **`/api/messages`** — GET/POST messages (dynamic endpoint)
- **`/api/echo/<name>`** — Dynamic route example

---

### 4 · CI Pipeline (GitHub Actions)

The pipeline is defined in `.github/workflows/ci-cd.yml` and runs automatically on every **push** or **pull request** to `main` or `dev`.

#### Jobs

| Job | Trigger | Steps |
|---|---|---|
| `lint` | Every push/PR | Checkout → Python setup → `flake8 app/` |
| `test` | After lint passes | Checkout → Install deps → `pytest tests/ -v` |
| `deploy` | After tests pass, **main branch only** | Deploy → Health check |

#### Running CI locally (act)

```bash
# Install act: https://github.com/nektos/act
act push
```

#### Running manually

```bash
# Lint
flake8 app/ --max-line-length=120 --ignore=E501

# Tests
pytest tests/ -v
```

**All 8 tests:**
```
tests/test_app.py::test_health_returns_ok          PASSED
tests/test_app.py::test_health_has_env             PASSED
tests/test_app.py::test_index_loads                PASSED
tests/test_app.py::test_post_message_success       PASSED
tests/test_app.py::test_post_message_missing_body  PASSED
tests/test_app.py::test_get_messages               PASSED
tests/test_app.py::test_dynamic_echo_route         PASSED
tests/test_app.py::test_echo_different_values      PASSED

======================== 8 passed in 0.24s ========================
```

---

### 5 · CD: Blue-Green Deployment

Blue-Green deployment maintains two identical production environments ("slots"). Only one slot is live at a time. A new version is deployed to the idle slot, health-checked, then traffic is switched atomically — zero downtime.

```
 Before deploy:          After deploy:
 ┌──────────┐           ┌──────────┐
 │  BLUE    │ ← LIVE    │  BLUE    │ (idle, old version)
 │  v1.0    │           │  v1.0    │
 └──────────┘           └──────────┘
 ┌──────────┐           ┌──────────┐
 │  GREEN   │ (idle)    │  GREEN   │ ← LIVE
 │  v1.0    │           │  v2.0    │ (new version)
 └──────────┘           └──────────┘
```

**Deploy a new version:**

```bash
bash scripts/deploy.sh v2.0
```

**What happens step-by-step:**

1. Reads `/opt/devops-demo/active_slot` → determines current live slot (e.g., `blue`)
2. Targets the idle slot (`green`)
3. Stops any running process in the idle slot
4. Copies new app code to the idle slot
5. Writes `VERSION` file with the version tag
6. Starts the new version on its port (`:5002`)
7. Polls `/health` up to 5 times — if unhealthy, aborts and keeps old slot live
8. Switches `active_slot` from `blue` → `green`
9. Records the release in `releases/history.jsonl`

**Expected output:**
```
[2024-05-01 12:00:00] 🚀 Deploying version v2.0
[2024-05-01 12:00:00]    Active slot: blue  (port 5001)
[2024-05-01 12:00:00]    Target slot: green (port 5002)
[2024-05-01 12:00:00] Starting green slot on port 5002...
[2024-05-01 12:00:00]    PID 12345 — waiting for startup...
[2024-05-01 12:00:02] ✅  green slot healthy
[2024-05-01 12:00:02] 🔀  Traffic switched: green is now LIVE on port 5002
[2024-05-01 12:00:02] 🎉  Deploy complete. Previous slot (blue:5001) standing by for rollback.
[2024-05-01 12:00:02]    Rollback: bash scripts/rollback.sh
```

---

### 6 · Rollback

If the new deployment has issues, roll back instantly to the previous slot:

```bash
bash scripts/rollback.sh
```

The rollback script:
1. Reads the current active slot
2. Checks if the previous slot's process is still running (it stays up as a warm standby)
3. If not running, restarts it from the already-deployed code
4. Health-checks the previous slot
5. Switches `active_slot` back atomically
6. Records the rollback event in `releases/history.jsonl`

**Expected output:**
```
[2024-05-01 12:05:00] ⏪  Rolling back: green → blue
[2024-05-01 12:05:00]    Previous slot (blue) already running on port 5001
[2024-05-01 12:05:00] ✅  Rollback complete. blue is now LIVE on port 5001
[2024-05-01 12:05:00]    (The failed deploy on green:5002 is now idle)
```

---

### 7 · Monitoring & Health Checks

#### One-time check

```bash
bash scripts/health_check.sh
```

**Output:**
```
[2024-05-01T12:10:00+0000] ── Health Check ────────────── active=green
[2024-05-01T12:10:00+0000]   SLOT=blue  PORT=5001  RESULT=DOWN  LATENCY=2ms
[2024-05-01T12:10:00+0000]   SLOT=green PORT=5002  STATUS=ok  VERSION=v2.0  ENV=production  LATENCY=14ms  RESULT=UP
[2024-05-01T12:10:00+0000]   OVERALL=HEALTHY  active=green
```

#### Continuous monitoring (watch mode)

```bash
bash scripts/health_check.sh --watch
# Checks every 30 seconds, logs to /var/log/devops-demo/health.log
```

#### Cron-based (recommended for production)

```bash
# Add to crontab (checks every minute):
* * * * * /opt/devops-demo/health_check.sh >> /var/log/devops-demo/health.log 2>&1
```

**View logs:**
```bash
tail -f /var/log/devops-demo/health.log
```

**Sample health log file (`/var/log/devops-demo/health.log`):**
```
[2024-05-01T12:00:00+0000] ── Health Check ────────────── active=blue
[2024-05-01T12:00:00+0000]   SLOT=blue  PORT=5001  STATUS=ok  VERSION=v1.0  ENV=production  LATENCY=12ms  RESULT=UP
[2024-05-01T12:00:00+0000]   SLOT=green PORT=5002  RESULT=DOWN  LATENCY=1ms
[2024-05-01T12:00:00+0000]   OVERALL=HEALTHY  active=blue
[2024-05-01T12:01:00+0000] ── Health Check ────────────── active=blue
[2024-05-01T12:01:00+0000]   SLOT=blue  PORT=5001  STATUS=ok  VERSION=v1.0  ENV=production  LATENCY=9ms  RESULT=UP
[2024-05-01T12:01:00+0000]   SLOT=green PORT=5002  RESULT=DOWN  LATENCY=1ms
[2024-05-01T12:01:00+0000]   OVERALL=HEALTHY  active=blue
[2024-05-01T12:05:03+0000] ── Health Check ────────────── active=green
[2024-05-01T12:05:03+0000]   SLOT=blue  PORT=5001  STATUS=ok  VERSION=v1.0  ENV=production  LATENCY=11ms  RESULT=UP
[2024-05-01T12:05:03+0000]   SLOT=green PORT=5002  STATUS=ok  VERSION=v2.0  ENV=production  LATENCY=13ms  RESULT=UP
[2024-05-01T12:05:03+0000]   OVERALL=HEALTHY  active=green
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `GET` | `/health` | Health check (JSON) |
| `GET` | `/api/messages` | List all messages |
| `POST` | `/api/messages` | Post a message `{"author":"...","body":"..."}` |
| `GET` | `/api/echo/<name>` | Dynamic echo route |

**Health check response:**
```json
{
  "status": "ok",
  "timestamp": "2024-05-01T12:00:00.000000",
  "version": "v2.0",
  "env": "production"
}
```

---

## Screenshots

> **Note:** Replace the placeholder sections below with actual screenshots from your deployed environment.

### ✅ CI Pipeline — GitHub Actions

Capture the Actions tab in your GitHub repo showing:
- All three jobs (`lint` → `test` → `deploy`) green
- The test output showing `8 passed`

```
[Screenshot: GitHub Actions — successful pipeline run]
All jobs green: lint ✅  test ✅  deploy ✅
```

### ✅ IaC Execution — Ansible / setup.sh

Capture your terminal output from:
```bash
ansible-playbook -i ansible/inventory.ini ansible/setup.yml
# or
bash setup.sh
```

```
[Screenshot: Terminal — Ansible PLAY RECAP showing ok=10 changed=9 failed=0]
```

### ✅ Deployment Process & Running App

Capture:
1. Terminal output of `bash scripts/deploy.sh v2.0`
2. Browser showing the app at `http://localhost:5002`
3. Browser showing `/health` JSON response

```
[Screenshot: deploy.sh output + running app in browser]
```

### ✅ Monitoring Logs

Capture:
```bash
tail -20 /var/log/devops-demo/health.log
```

```
[Screenshot: health.log showing periodic checks with RESULT=UP entries]
```

---

## Quick Reference

```bash
# Full setup (one command)
bash setup.sh

# Run tests
pytest tests/ -v

# Lint
flake8 app/ --max-line-length=120

# Start app
APP_ENV=production PORT=5001 python3 app/app.py

# Deploy new version
bash scripts/deploy.sh v2.0

# Rollback
bash scripts/rollback.sh

# Health check (once)
bash scripts/health_check.sh

# Health check (continuous)
bash scripts/health_check.sh --watch
```
