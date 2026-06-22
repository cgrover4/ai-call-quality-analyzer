from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import schemas
from analytics import (
    build_region_analytics,
    build_summary,
    enrich_call,
    flag_call_issues,
)
from database import get_db, init_db
from models import CallSession
from seed_data import generate_seed_calls


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Call Quality Analyzer",
    description=(
        "Carrier-grade telecommunications analytics API for simulated VoIP call "
        "quality monitoring across distributed regions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "service": "AI Call Quality Analyzer",
        "status": "online",
        "docs": "/docs",
        "endpoints": [
            "POST /calls",
            "GET /calls",
            "GET /calls/{call_id}",
            "GET /analytics/summary",
            "GET /analytics/regions",
            "GET /analytics/problems",
            "POST /seed",
        ],
    }


@app.post(
    "/calls",
    response_model=schemas.CallRead,
    status_code=status.HTTP_201_CREATED,
)
def create_call(call: schemas.CallCreate, db: Session = Depends(get_db)):
    call_data = call.model_dump()
    call_data["call_id"] = call_data["call_id"] or f"CALL-{uuid4().hex[:12].upper()}"

    db_call = CallSession(**call_data)
    db.add(db_call)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Call with call_id '{call_data['call_id']}' already exists.",
        ) from exc

    db.refresh(db_call)
    return enrich_call(db_call)


@app.get("/calls", response_model=list[schemas.CallRead])
def list_calls(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=10000),
    region: schemas.Region | None = Query(default=None),
    status_filter: schemas.CallStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(CallSession)

    if region:
        query = query.filter(CallSession.region == region)

    if status_filter:
        query = query.filter(CallSession.status == status_filter)

    calls = (
        query.order_by(CallSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [enrich_call(call) for call in calls]


@app.get("/calls/{call_id}", response_model=schemas.CallRead)
def get_call(call_id: str, db: Session = Depends(get_db)):
    call = db.query(CallSession).filter(CallSession.call_id == call_id).first()

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call with call_id '{call_id}' was not found.",
        )

    return enrich_call(call)


@app.get("/analytics/summary", response_model=schemas.SummaryAnalytics)
def get_summary(db: Session = Depends(get_db)):
    calls = db.query(CallSession).all()
    return build_summary(calls)


@app.get("/analytics/regions", response_model=list[schemas.RegionAnalytics])
def get_region_analytics(db: Session = Depends(get_db)):
    calls = db.query(CallSession).all()
    return build_region_analytics(calls)


@app.get("/analytics/problems", response_model=list[schemas.ProblemCall])
def get_problem_calls(
    max_quality_score: int = Query(default=75, ge=0, le=100),
    limit: int = Query(default=100, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    calls = db.query(CallSession).all()
    enriched_calls = [enrich_call(call) for call in calls]
    problem_calls = [
        call
        for call in enriched_calls
        if call["quality_score"] <= max_quality_score or call["problem_flags"]
    ]

    return sorted(problem_calls, key=lambda call: call["quality_score"])[:limit]


@app.post("/seed", response_model=schemas.SeedResponse)
def seed_database(
    count: int = Query(default=1000, ge=1000, le=10000),
    db: Session = Depends(get_db),
):
    calls = generate_seed_calls(count=count)
    db.add_all(calls)
    db.commit()

    return {
        "inserted_records": len(calls),
        "total_records": db.query(CallSession).count(),
        "message": (
            f"Inserted {len(calls)} simulated VoIP call records across "
            "us-west, us-east, eu-central, and ap-south."
        ),
    }
