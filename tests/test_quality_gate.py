import os
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/check_quality.py"


@pytest.mark.parametrize("score,accepted", [
    ("0.6499", False), ("0.65", True), ("0.7149321266968326", True),
    ("1.0", True), ("1.01", False), ("nan", False), ("inf", False), ("", False),
])
def test_quality_gate_accepts_only_valid_passing_f1(score, accepted):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        env={**os.environ, "F1_SCORE": score}, capture_output=True, text=True,
    )
    assert (result.returncode == 0) is accepted
