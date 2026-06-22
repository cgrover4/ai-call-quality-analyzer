from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from database import Base


class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True, index=True, nullable=False)
    caller = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    region = Column(String, index=True, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    jitter_ms = Column(Float, nullable=False)
    packet_loss_percent = Column(Float, nullable=False)
    throughput_kbps = Column(Float, nullable=False)
    status = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
