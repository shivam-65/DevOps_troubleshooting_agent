import hashlib
import random
import string
import uuid
from typing import List, Optional


def seeded_random(seed: Optional[str] = None) -> random.Random:
    if seed:
        int_seed = int(hashlib.md5(seed.encode()).hexdigest(), 16) % (2**32)
        return random.Random(int_seed)
    return random.Random()


def random_pod_suffix(rng: random.Random = None) -> str:
    rng = rng or random.Random()
    part1 = "".join(rng.choices(string.ascii_lowercase + string.digits, k=5))
    part2 = "".join(rng.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{part1}-{part2}"


def random_sha(rng: random.Random = None) -> str:
    rng = rng or random.Random()
    return "".join(rng.choices("0123456789abcdef", k=12))


def random_trace_id(rng: random.Random = None) -> str:
    rng = rng or random.Random()
    return "".join(rng.choices("0123456789abcdef", k=16))


def random_ip(rng: random.Random = None) -> str:
    rng = rng or random.Random()
    return f"10.0.{rng.randint(0, 255)}.{rng.randint(1, 254)}"


def jitter(value: float, percent: float = 5.0, rng: random.Random = None) -> float:
    """Add random noise (±percent%) to a value."""
    rng = rng or random.Random()
    factor = 1.0 + rng.uniform(-percent / 100, percent / 100)
    return round(value * factor, 2)


def pick_random(items: List, rng: random.Random = None):
    rng = rng or random.Random()
    return rng.choice(items) if items else None


def random_uuid() -> str:
    return str(uuid.uuid4())
