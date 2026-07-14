from datetime import datetime, timedelta, timezone
from typing import Optional


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def parse_duration(duration_str: str) -> timedelta:
    """Parse simple duration strings like '1h', '30m', '24h', 'PT30M'."""
    duration_str = duration_str.strip().upper()
    if duration_str.startswith("PT"):
        duration_str = duration_str[2:]
        total = timedelta()
        num = ""
        for ch in duration_str:
            if ch.isdigit() or ch == ".":
                num += ch
            elif ch == "H":
                total += timedelta(hours=float(num))
                num = ""
            elif ch == "M":
                total += timedelta(minutes=float(num))
                num = ""
            elif ch == "S":
                total += timedelta(seconds=float(num))
                num = ""
        return total
    if duration_str.endswith("H"):
        return timedelta(hours=float(duration_str[:-1]))
    if duration_str.endswith("M"):
        return timedelta(minutes=float(duration_str[:-1]))
    if duration_str.endswith("S"):
        return timedelta(seconds=float(duration_str[:-1]))
    if duration_str.endswith("D"):
        return timedelta(days=float(duration_str[:-1]))
    return timedelta(hours=1)


def default_since(since: Optional[str], default_hours: int = 1) -> datetime:
    parsed = parse_iso(since)
    if parsed:
        return parsed
    return now_utc() - timedelta(hours=default_hours)


def default_until(until: Optional[str]) -> datetime:
    parsed = parse_iso(until)
    if parsed:
        return parsed
    return now_utc()


def parse_step(step: str) -> timedelta:
    """Parse step strings like '1m', '5m', '15m'."""
    step = step.strip().lower()
    if step.endswith("m"):
        return timedelta(minutes=int(step[:-1]))
    if step.endswith("h"):
        return timedelta(hours=int(step[:-1]))
    if step.endswith("s"):
        return timedelta(seconds=int(step[:-1]))
    return timedelta(minutes=1)


def format_duration(td: timedelta) -> str:
    """Format a timedelta as ISO 8601 duration string."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = ["PT"]
    if hours:
        parts.append(f"{hours}H")
    if minutes:
        parts.append(f"{minutes}M")
    if seconds or not (hours or minutes):
        parts.append(f"{seconds}S")
    return "".join(parts)
