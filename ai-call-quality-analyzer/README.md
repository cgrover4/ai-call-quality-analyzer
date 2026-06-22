# AI Call Quality Analyzer

AI Call Quality Analyzer is a beginner-friendly full-stack application that simulates and analyzes VoIP call quality across geographically distributed telecom regions. It stores call sessions in SQLite, calculates a 0-100 quality score, flags network problems, generates simple AI-style root-cause explanations using rule-based analytics, and displays the results in a polished React dashboard.

The project is designed to feel like a small carrier-grade telecommunications analytics platform while staying easy to run locally.

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Uvicorn
- React
- Vite
- Chart.js

## Project Structure

```text
ai-call-quality-analyzer/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── analytics.py
├── seed_data.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── main.jsx
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup Instructions

### Backend API

1. Go into the project directory:

   ```bash
   cd ai-call-quality-analyzer
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the API server:

   ```bash
   uvicorn main:app --reload
   ```

5. Open the interactive API docs:

   ```text
   http://127.0.0.1:8000/docs
   ```

The SQLite database file `call_quality.db` is created automatically when the application starts.

The backend includes CORS support for the Vite frontend at `http://localhost:5173` and `http://127.0.0.1:5173`.

### Frontend Dashboard

Open a second terminal while the backend is still running.

1. Go into the frontend directory:

   ```bash
   cd ai-call-quality-analyzer/frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the Vite development server:

   ```bash
   npm run dev
   ```

4. Open the dashboard:

   ```text
   http://localhost:5173
   ```

The dashboard calls the FastAPI backend at `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Service health and endpoint overview |
| `POST` | `/calls` | Create a simulated VoIP call session |
| `GET` | `/calls` | List call sessions with optional pagination, region, and status filters |
| `GET` | `/calls/{call_id}` | Get one call session by external call ID |
| `GET` | `/analytics/summary` | Get overall call quality metrics and problem counts |
| `GET` | `/analytics/regions` | Get analytics grouped by region |
| `GET` | `/analytics/problems` | Get low-quality or problematic calls |
| `POST` | `/seed` | Insert at least 1000 realistic simulated VoIP call records |

### Optional Query Parameters

`GET /calls`

- `skip`: number of records to skip, default `0`
- `limit`: number of records to return, default `100`, maximum `10000`
- `region`: one of `us-west`, `us-east`, `eu-central`, `ap-south`
- `status`: one of `completed`, `dropped`, `failed`

`GET /analytics/problems`

- `max_quality_score`: quality score threshold, default `75`
- `limit`: number of problem calls to return, default `100`, maximum `10000`

`POST /seed`

- `count`: number of records to insert, default `1000`, minimum `1000`, maximum `10000`

## Example JSON Payload

Use this body with `POST /calls`:

```json
{
  "call_id": "CALL-DEMO-001",
  "caller": "+14155550100",
  "receiver": "+442071838750",
  "region": "us-west",
  "duration_seconds": 180,
  "latency_ms": 82.5,
  "jitter_ms": 9.8,
  "packet_loss_percent": 0.4,
  "throughput_kbps": 465.0,
  "status": "completed"
}
```

The `call_id` field is optional. If it is not provided, the API generates one automatically.

## Example Workflow

Start the API:

```bash
uvicorn main:app --reload
```

Seed the database:

```bash
curl -X POST "http://127.0.0.1:8000/seed"
```

View summary analytics:

```bash
curl "http://127.0.0.1:8000/analytics/summary"
```

View regional analytics:

```bash
curl "http://127.0.0.1:8000/analytics/regions"
```

Find problem calls:

```bash
curl "http://127.0.0.1:8000/analytics/problems?max_quality_score=75"
```

Run the frontend dashboard:

```bash
cd frontend
npm install
npm run dev
```

## Analytics Logic

The application calculates a call quality score from `0` to `100` by applying deductions for:

- high latency
- high jitter
- high packet loss
- low throughput
- dropped or failed calls

It also flags problem categories:

- `high_latency`
- `high_jitter`
- `high_packet_loss`
- `low_throughput`
- `call_failure`

Each call response includes:

- `quality_score`
- `problem_flags`
- `root_cause`

The root-cause explanation is rule-based and written in an AI-style format so the project can demonstrate analytics behavior without requiring an external AI service.

## Resume Bullet Points

- Built a full-stack telecommunications analytics platform for simulated VoIP call quality monitoring across distributed regions.
- Designed a SQLite and SQLAlchemy data model for latency, jitter, packet loss, throughput, duration, call status, and timestamps.
- Implemented REST APIs for call ingestion, retrieval, summary analytics, regional analytics, problem detection, and bulk seeding.
- Created rule-based AI-style diagnostics that score call quality and explain likely root causes for degraded calls.
- Generated realistic seed data for 1000+ VoIP sessions across `us-west`, `us-east`, `eu-central`, and `ap-south`.
- Developed a modern React, Vite, and Chart.js dashboard with KPI cards, regional charts, poor-call distribution, seed controls, and responsive dark-theme styling.
