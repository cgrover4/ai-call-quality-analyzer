from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Region = Literal["us-west", "us-east", "eu-central", "ap-south"]
CallStatus = Literal["completed", "dropped", "failed"]


class CallCreate(BaseModel):
    call_id: str | None = Field(
        default=None,
        min_length=3,
        max_length=80,
        description="Optional external call identifier. A UUID-based value is generated when omitted.",
    )
    caller: str = Field(..., min_length=3, max_length=40, examples=["+14155550100"])
    receiver: str = Field(..., min_length=3, max_length=40, examples=["+442071838750"])
    region: Region = Field(..., examples=["us-west"])
    duration_seconds: int = Field(..., ge=1, le=24 * 60 * 60, examples=[180])
    latency_ms: float = Field(..., ge=0, examples=[85.5])
    jitter_ms: float = Field(..., ge=0, examples=[12.2])
    packet_loss_percent: float = Field(..., ge=0, le=100, examples=[0.5])
    throughput_kbps: float = Field(..., ge=0, examples=[420.0])
    status: CallStatus = Field(default="completed", examples=["completed"])


class CallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    call_id: str
    caller: str
    receiver: str
    region: str
    duration_seconds: int
    latency_ms: float
    jitter_ms: float
    packet_loss_percent: float
    throughput_kbps: float
    status: str
    created_at: datetime
    quality_score: int
    problem_flags: list[str]
    root_cause: str


class SummaryAnalytics(BaseModel):
    total_calls: int
    completed_calls: int
    dropped_calls: int
    failed_calls: int
    average_quality_score: float
    average_latency_ms: float
    average_jitter_ms: float
    average_packet_loss_percent: float
    average_throughput_kbps: float
    problem_counts: dict[str, int]


class RegionAnalytics(BaseModel):
    region: str
    total_calls: int
    completed_calls: int
    dropped_calls: int
    failed_calls: int
    average_quality_score: float
    average_latency_ms: float
    average_jitter_ms: float
    average_packet_loss_percent: float
    average_throughput_kbps: float
    top_problem: str | None


class ProblemCall(BaseModel):
    call_id: str
    caller: str
    receiver: str
    region: str
    status: str
    quality_score: int
    problem_flags: list[str]
    root_cause: str


class SeedResponse(BaseModel):
    inserted_records: int
    total_records: int
    message: str
