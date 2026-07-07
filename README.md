# CitySage

A smart city dashboard for the Washington, DC / Maryland region. CitySage combines
real-time highway traffic detection, WMATA transit alerts, weather, and AI-generated
traffic summaries into a single live dashboard.

🌐 **Live at [citysage.net](https://citysage.net)**

## Features

### 🚦 Traffic Monitoring
- Real-time vehicle detection using computer vision (Roboflow YOLOv8) on Maryland
  DOT highway camera streams
- Virtual line-crossing counting across 11 cameras on I-95, I-495, and I-270
- Round-robin scheduling and per-minute counts logged to PostgreSQL
- Live HLS video feeds streamed directly from Maryland SHA to the browser

### 🚌 Transit Intelligence
- WMATA (Washington Metro) real-time bus and rail incident alerts
- Severity classification (critical / major / minor) from incident content

### 🌤️ Weather
- Current conditions and daily forecast for Washington, DC (via WeatherAPI)

### 🤖 AI Traffic Summaries
- Plain-English summaries of traffic conditions generated with OpenAI (gpt-4.1-nano)
- Hourly breakdown so summaries describe how traffic changes through the day
  (rush-hour peaks vs. overnight lulls)
- Deterministic fallback summary when no AI key is configured

## Technology Stack

### Backend
- **Flask** — Python web framework (API under `/api`)
- **Roboflow `inference`** — YOLOv8 vehicle detection (runs locally on the host)
- **PostgreSQL** (`psycopg2`) — per-minute vehicle counts
- **OpenAI** — AI traffic summaries
- **Multithreading** — concurrent camera processing with round-robin scheduling

### Frontend
- **React + TypeScript**, **Vite**
- **Tailwind CSS** + **shadcn/ui**
- **Framer Motion** — animations
- **HLS.js** — live video streaming

### Infrastructure (AWS)
- **EC2** — Flask API + inference workers, managed via **AWS Systems Manager (SSM)** (no open SSH)
- **RDS PostgreSQL** — traffic count storage
- **S3 + CloudFront** — frontend hosting and CDN over HTTPS
- **ACM** — TLS certificate for citysage.net
- **GitHub Actions** — CI/CD (see below)

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A PostgreSQL database
- API keys: Roboflow, WMATA, OpenAI (optional), WeatherAPI (frontend)

### Installation

1. Clone the repository.
2. Set up the backend:
   ```bash
   cd backend
   python3.11 -m venv venv && source venv/bin/activate
   pip install -r ../requirements.txt
   ```
3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```
4. Create `backend/.env` with the environment variables below.

### Environment Variables

Backend (`backend/.env`):
```
ROBOFLOW_API_KEY=...            # vehicle detection model
WMATA_API_KEY=...               # transit alerts
OPENAI_KEY=...                  # AI summaries (optional; falls back if unset)
OPENAI_ENDPOINT=https://api.openai.com/v1
DB_NAME=... DB_USER=... DB_PASSWORD=... DB_HOST=... DB_PORT=5432

# Optional tuning (defaults shown)
DETECTION_MAX_FPS=1             # inference frames/sec per camera
CONCURRENT_CAMERAS=3            # cameras inferring at once (round-robin)
ACTIVE_WINDOW_SECONDS=120       # seconds per camera group before cycling
DB_FLUSH_INTERVAL_SECONDS=600   # how often buffered counts are batch-written
FLASK_DEBUG=0                   # set to 1 for local debugging only
```

Frontend (`frontend/.env`):
```
VITE_WEATHER_API_KEY=...
```

The database needs a `vehicle_counts` table:
```sql
CREATE TABLE IF NOT EXISTS vehicle_counts (
  camera_id TEXT NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (camera_id, timestamp)
);
```

### Running the Application

**Development:**
```bash
# Backend — run as a module from the repo root (uses absolute `backend.*` imports)
python -m backend.app

# Frontend
cd frontend && npm run dev   # proxies /api to the backend
```

## CI/CD

Deployment is automated with **GitHub Actions** (`.github/workflows/deploy.yml`).
On every push to `main`:

1. GitHub authenticates to AWS using a scoped IAM user (permitted only
   `ssm:SendCommand` to the one EC2 instance — no SSH port is opened).
2. It sends a deploy script to the instance via **AWS Systems Manager**, which
   pulls the latest `main`, reinstalls dependencies, and restarts the
   `citysage` systemd service.
3. The workflow polls the SSM command until it reports success.

Manual runs are supported via the workflow's `workflow_dispatch` trigger.

Required GitHub repository secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_REGION`, `EC2_INSTANCE_ID`.

## Architecture

```
Browser ──HTTPS──> CloudFront ──┬── /*      ──> S3 (React frontend)
                                └── /api/*  ──> EC2 (Flask API + inference)
                                                   ├── Roboflow YOLOv8 (round-robin, per-minute counts)
                                                   ├── RDS PostgreSQL (vehicle_counts)
                                                   ├── WMATA Incidents API (transit alerts)
                                                   └── OpenAI (traffic summaries)

Live HLS video streams flow directly from Maryland SHA to the browser.
```

## Project Structure

```
CitySage/
├── backend/                      # Python Flask API
│   ├── app.py                    # entrypoint (run as `python -m backend.app`)
│   ├── traffic/detection/        # CV detection, round-robin scheduler, DB, summaries
│   ├── traffic/config/           # camera configurations
│   └── scrapers/                 # WMATA alert routes
├── frontend/                     # React + TypeScript (Vite) app
│   └── src/
│       ├── components/dashboard/ # dashboard cards
│       ├── pages/                # application pages
│       └── hooks/                # custom React hooks
└── .github/workflows/deploy.yml  # CI/CD (deploy to EC2 via SSM)
```

## Contributing

This project is part of University of Maryland research into smart city
infrastructure and urban data analytics.
