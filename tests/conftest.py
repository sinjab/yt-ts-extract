import pytest


@pytest.fixture
def sample_transcript():
    return [
        {"text": "Hello world this is a test", "start": 1.2, "duration": 2.8},
        {"text": "We test utilities and extractor", "start": 5.0, "duration": 4.0},
        {"text": "Final segment with keywords and more text", "start": 11.5, "duration": 3.5},
    ]
