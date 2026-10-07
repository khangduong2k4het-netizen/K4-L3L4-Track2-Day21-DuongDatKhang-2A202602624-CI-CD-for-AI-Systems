"""Reject invalid scores as well as scores below the lab threshold."""
import math
import os

try:
    score = float(os.environ["F1_SCORE"])
except (KeyError, ValueError) as error:
    raise SystemExit("FAILED: missing or invalid f1_score") from error
if not math.isfinite(score) or not 0.65 <= score <= 1.0:
    raise SystemExit(f"FAILED: f1_score {score} must be between 0.65 and 1.0. Deployment cancelled.")
print(f"PASSED: f1_score {score:.4f} >= 0.65")
