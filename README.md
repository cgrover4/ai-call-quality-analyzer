# AI Call Quality Analyzer

AI Call Quality Analyzer is a FastAPI-based telecommunications analytics backend that simulates and analyzes VoIP call sessions across geographically distributed regions. The platform evaluates call quality using latency, jitter, packet loss, throughput, duration, region, and failure status to identify poor call experiences and network reliability issues.

This project is designed to demonstrate backend engineering, REST API development, SQLite data storage, telecom-style metrics analysis, and rule-based AI-style root cause explanations.

---

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Uvicorn
- REST APIs

---

## Key Features

- Simulates realistic VoIP call session records
- Stores call session data in SQLite
- Calculates call quality scores from 0 to 100
- Detects high latency, jitter, packet loss, low throughput, dropped calls, and failed calls
- Generates AI-style root cause explanations using rule-based analytics
- Provides regional health analysis across distributed regions
- Exposes REST APIs for call ingestion, lookup, summaries, and problem detection
- Includes seed data generation for testing with large call volumes

---

## Why This Project Matters

Modern telecommunications platforms must process large volumes of real-time communication data while maintaining reliability, low latency, and high availability. This project simulates a small-scale version of that environment by analyzing VoIP call quality metrics across distributed regions.

It is inspired by real-world telecom engineering challenges such as:

- Call quality monitoring
- Latency and jitter analysis
- Packet loss detection
- Regional reliability tracking
- Root cause analysis
- Backend API reliability
- Platform observability

---

## Project Structure

```text
ai-call-quality-analyzer/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── analytics.py
├── requirements.txt
├── README.md
└── .gitignore
