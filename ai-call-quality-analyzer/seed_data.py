import random
from datetime import datetime, timedelta
from uuid import uuid4

from models import CallSession


REGIONS = ["us-west", "us-east", "eu-central", "ap-south"]

REGION_PROFILES = {
    "us-west": {
        "latency_ms": (55, 18),
        "jitter_ms": (8, 4),
        "packet_loss_percent": (0.25, 0.25),
        "throughput_kbps": (520, 130),
    },
    "us-east": {
        "latency_ms": (65, 20),
        "jitter_ms": (10, 5),
        "packet_loss_percent": (0.35, 0.30),
        "throughput_kbps": (500, 125),
    },
    "eu-central": {
        "latency_ms": (80, 24),
        "jitter_ms": (13, 6),
        "packet_loss_percent": (0.45, 0.35),
        "throughput_kbps": (455, 120),
    },
    "ap-south": {
        "latency_ms": (115, 35),
        "jitter_ms": (18, 8),
        "packet_loss_percent": (0.75, 0.55),
        "throughput_kbps": (380, 140),
    },
}


def _positive_gauss(mean: float, deviation: float, minimum: float = 0) -> float:
    return max(minimum, random.gauss(mean, deviation))


def _random_phone_number() -> str:
    country_code = random.choice(["+1", "+44", "+49", "+91"])
    local_number = random.randint(1000000000, 9999999999)
    return f"{country_code}{local_number}"


def _status_for_call(has_incident: bool) -> str:
    if has_incident:
        return random.choices(
            ["completed", "dropped", "failed"],
            weights=[70, 18, 12],
            k=1,
        )[0]

    return random.choices(
        ["completed", "dropped", "failed"],
        weights=[94, 4, 2],
        k=1,
    )[0]


def generate_seed_calls(count: int = 1000) -> list[CallSession]:
    calls = []

    for _ in range(count):
        region = random.choice(REGIONS)
        profile = REGION_PROFILES[region]
        has_incident = random.random() < 0.14

        latency_ms = _positive_gauss(*profile["latency_ms"])
        jitter_ms = _positive_gauss(*profile["jitter_ms"])
        packet_loss_percent = _positive_gauss(*profile["packet_loss_percent"])
        throughput_kbps = _positive_gauss(*profile["throughput_kbps"], minimum=20)

        if has_incident:
            latency_ms += random.uniform(70, 220)
            jitter_ms += random.uniform(20, 75)
            packet_loss_percent += random.uniform(1.5, 8.0)
            throughput_kbps *= random.uniform(0.15, 0.55)

        status = _status_for_call(has_incident)
        duration_seconds = random.randint(15, 3600)
        if status == "failed":
            duration_seconds = random.randint(1, 60)
        elif status == "dropped":
            duration_seconds = random.randint(10, 900)

        calls.append(
            CallSession(
                call_id=f"CALL-{uuid4().hex[:12].upper()}",
                caller=_random_phone_number(),
                receiver=_random_phone_number(),
                region=region,
                duration_seconds=duration_seconds,
                latency_ms=round(latency_ms, 2),
                jitter_ms=round(jitter_ms, 2),
                packet_loss_percent=round(min(packet_loss_percent, 100), 2),
                throughput_kbps=round(throughput_kbps, 2),
                status=status,
                created_at=datetime.utcnow()
                - timedelta(minutes=random.randint(0, 60 * 24 * 30)),
            )
        )

    return calls
