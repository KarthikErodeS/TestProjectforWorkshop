import pytest
from fastapi.testclient import TestClient
from main import app
import json

# Mock questions data
mock_questions = [
    {
        "id": 1,
        "question": "Q1",
        "choices": [
            {"text": "A1", "is_correct": True},
            {"text": "B1", "is_correct": False}
        ]
    },
    {
        "id": 2,
        "question": "Q2",
        "choices": [
            {"text": "A2", "is_correct": True},
            {"text": "B2", "is_correct": False}
        ]
    },
    {
        "id": 3,
        "question": "Q3",
        "choices": [
            {"text": "A3", "is_correct": True},
            {"text": "B3", "is_correct": False}
        ]
    },
    {
        "id": 4,
        "question": "Q4",
        "choices": [
            {"text": "A4", "is_correct": True},
            {"text": "B4", "is_correct": False}
        ]
    },
    {
        "id": 5,
        "question": "Q5",
        "choices": [
            {"text": "A5", "is_correct": True},
            {"text": "B5", "is_correct": False}
        ]
    },
    {
        "id": 6,
        "question": "Q6",
        "choices": [
            {"text": "A6", "is_correct": True},
            {"text": "B6", "is_correct": False}
        ]
    },
]

client = TestClient(app)

# Patch reading of questions.json
import builtins

def mock_open(*args, **kwargs):
    filename = str(args[0])
    if filename.endswith('questions.json'):
        return MockFile(json.dumps(mock_questions))
    return open_orig(*args, **kwargs)

class MockFile:
    def __init__(self, data):
        self.data = data
        self._lines = [data]
    def read(self):
        return self.data
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def readline(self):
        return self.data
    def readlines(self):
        return self._lines

open_orig = builtins.open

@pytest.fixture(autouse=True)
def patch_open(monkeypatch):
    monkeypatch.setattr(builtins, "open", mock_open)


def test_get_assessment():
    response = client.get("/assessment")
    assert response.status_code == 200
    for q in mock_questions:
        assert q["question"] in response.text


def test_post_submit_redirect():
    answers = {f"answers{idx+1}": next(c["text"] for c in q["choices"] if c["is_correct"]) for idx, q in enumerate(mock_questions)}
    response = client.post("/submit", data=answers, follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/result" in response.headers["location"]


def test_result_page():
    # Submit answers first
    answers = {f"answers{idx+1}": next(c["text"] for c in q["choices"] if c["is_correct"]) for idx, q in enumerate(mock_questions)}
    client.post("/submit", data=answers)
    response = client.get("/result")
    assert response.status_code == 200
    assert "Your Score" in response.text


def test_score_calculation():
    # All correct
    answers = {f"answers{idx+1}": next(c["text"] for c in q["choices"] if c["is_correct"]) for idx, q in enumerate(mock_questions)}
    client.post("/submit", data=answers)
    response = client.get("/result")
    print(response.text)  # Debug: print actual response
    assert "6" in response.text and "/ 6" in response.text
    # All incorrect
    wrong_answers = {f"answers{idx+1}": "wrong" for idx, q in enumerate(mock_questions)}
    client.post("/submit", data=wrong_answers)
    response = client.get("/result")
    assert "0" in response.text and "/ 6" in response.text
