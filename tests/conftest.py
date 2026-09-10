import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_standard_data.json")


@pytest.fixture
def sample_data():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return copy.deepcopy(json.load(f))
