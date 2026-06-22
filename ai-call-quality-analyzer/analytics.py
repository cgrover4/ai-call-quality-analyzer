from collections import Counter
from statistics import mean
from typing import Any


HIGH_LATENCY_MS = 150.0
HIGH_JITTER_MS = 30.0
HIGH_PACKET_LOSS_PERCENT = 2.0
LOW_THROUGHPUT_KBPS = 100.0


def _value(call: Any, field_name: str):
    if isinstance(call, dict):
        return call[field_name]
    return getattr(call, field_name)


def calculate_quality_score(call: Any) -> int:
    """Calculate a voice quality score from 0 to 100 using telecom health metrics."""
    score = 100.0

    latency_ms = _value(call, "latency_ms")
    jitter_ms = _value(call, "jitter_ms")
    packet_loss_percent = _value(call, "packet_loss_percent")
    throughput_kbps = _value(call, "throughput_kbps")
    status = _value(call, "status")

    if latency_ms > 100:
        score -= min(30, (latency_ms - 100) * 0.12)

    if jitter_ms > 20:
        score -= min(20, (jitter_ms - 20) * 0.40)

    if packet_loss_percent > 1:
        score -= min(30, packet_loss_percent * 8)

    if throughput_kbps < 300:
        score -= min(20, (300 - throughput_kbps) * 0.05)

    if status == "dropped":
        score -= 25
    elif status == "failed":
        score -= 35

    return max(0, min(100, round(score)))


def flag_call_issues(call: Any) -> list[str]:
    flags = []

    if _value(call, "latency_ms") >= HIGH_LATENCY_MS:
        flags.append("high_latency")

    if _value(call, "jitter_ms") >= HIGH_JITTER_MS:
        flags.append("high_jitter")

    if _value(call, "packet_loss_percent") >= HIGH_PACKET_LOSS_PERCENT:
        flags.append("high_packet_loss")

    if _value(call, "throughput_kbps") <= LOW_THROUGHPUT_KBPS:
        flags.append("low_throughput")

    if _value(call, "status") in {"dropped", "failed"}:
        flags.append("call_failure")

    return flags


def generate_root_cause(call: Any) -> str:
    flags = set(flag_call_issues(call))
    region = _value(call, "region")
    status = _value(call, "status")

    if not flags:
        return (
            "No major quality issue detected. The call completed with stable latency, "
            "jitter, packet delivery, and throughput."
        )

    if "call_failure" in flags and {"high_packet_loss", "low_throughput"} & flags:
        return (
            f"The {status} call in {region} was likely caused by network congestion or "
            "access-link saturation, shown by packet loss or reduced throughput."
        )

    if {"high_latency", "high_jitter", "high_packet_loss"}.issubset(flags):
        return (
            f"The call path in {region} shows end-to-end instability. High latency, "
            "jitter, and packet loss together point to routing congestion or an "
            "overloaded regional media gateway."
        )

    if "high_latency" in flags and "high_jitter" in flags:
        return (
            f"The call likely used an unstable or long-distance route through {region}. "
            "Latency and jitter spikes can cause delayed audio and choppy speech."
        )

    if "high_packet_loss" in flags:
        return (
            f"Packet loss is the primary quality driver in {region}. RTP media packets "
            "may be dropped by congested links, queues, or unreliable last-mile access."
        )

    if "low_throughput" in flags:
        return (
            f"Available bandwidth in {region} appears constrained. Low throughput can "
            "force codec degradation and increase the risk of call drops."
        )

    if "call_failure" in flags:
        return (
            f"The call ended with status '{status}'. Signaling, routing, or endpoint "
            "availability should be checked even though media metrics were acceptable."
        )

    return (
        f"The call has moderate quality degradation in {region}. Review media routing, "
        "gateway capacity, and endpoint network conditions."
    )


def enrich_call(call: Any) -> dict[str, Any]:
    return {
        "id": _value(call, "id"),
        "call_id": _value(call, "call_id"),
        "caller": _value(call, "caller"),
        "receiver": _value(call, "receiver"),
        "region": _value(call, "region"),
        "duration_seconds": _value(call, "duration_seconds"),
        "latency_ms": _value(call, "latency_ms"),
        "jitter_ms": _value(call, "jitter_ms"),
        "packet_loss_percent": _value(call, "packet_loss_percent"),
        "throughput_kbps": _value(call, "throughput_kbps"),
        "status": _value(call, "status"),
        "created_at": _value(call, "created_at"),
        "quality_score": calculate_quality_score(call),
        "problem_flags": flag_call_issues(call),
        "root_cause": generate_root_cause(call),
    }


def build_summary(calls: list[Any]) -> dict[str, Any]:
    if not calls:
        return {
            "total_calls": 0,
            "completed_calls": 0,
            "dropped_calls": 0,
            "failed_calls": 0,
            "average_quality_score": 0,
            "average_latency_ms": 0,
            "average_jitter_ms": 0,
            "average_packet_loss_percent": 0,
            "average_throughput_kbps": 0,
            "problem_counts": {},
        }

    status_counts = Counter(_value(call, "status") for call in calls)
    problem_counts = Counter(
        flag for call in calls for flag in flag_call_issues(call)
    )

    return {
        "total_calls": len(calls),
        "completed_calls": status_counts["completed"],
        "dropped_calls": status_counts["dropped"],
        "failed_calls": status_counts["failed"],
        "average_quality_score": round(mean(calculate_quality_score(call) for call in calls), 2),
        "average_latency_ms": round(mean(_value(call, "latency_ms") for call in calls), 2),
        "average_jitter_ms": round(mean(_value(call, "jitter_ms") for call in calls), 2),
        "average_packet_loss_percent": round(
            mean(_value(call, "packet_loss_percent") for call in calls),
            2,
        ),
        "average_throughput_kbps": round(
            mean(_value(call, "throughput_kbps") for call in calls),
            2,
        ),
        "problem_counts": dict(problem_counts),
    }


def build_region_analytics(calls: list[Any]) -> list[dict[str, Any]]:
    grouped_calls: dict[str, list[Any]] = {}
    for call in calls:
        grouped_calls.setdefault(_value(call, "region"), []).append(call)

    analytics = []
    for region, region_calls in sorted(grouped_calls.items()):
        summary = build_summary(region_calls)
        problem_counts = summary["problem_counts"]
        top_problem = None
        if problem_counts:
            top_problem = max(problem_counts, key=problem_counts.get)

        analytics.append(
            {
                "region": region,
                "total_calls": summary["total_calls"],
                "completed_calls": summary["completed_calls"],
                "dropped_calls": summary["dropped_calls"],
                "failed_calls": summary["failed_calls"],
                "average_quality_score": summary["average_quality_score"],
                "average_latency_ms": summary["average_latency_ms"],
                "average_jitter_ms": summary["average_jitter_ms"],
                "average_packet_loss_percent": summary["average_packet_loss_percent"],
                "average_throughput_kbps": summary["average_throughput_kbps"],
                "top_problem": top_problem,
            }
        )

    return analytics
