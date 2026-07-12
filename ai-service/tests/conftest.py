import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("BACKEND_BASE_URL", "http://localhost:8080")
