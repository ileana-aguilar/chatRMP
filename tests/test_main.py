import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_best_professor_query():
    response = client.post("/search_professors", json={"query": "Who is the best professor in Computer Science?"})
    assert response.status_code == 200
    assert "Best professor in" in response.json()["response"]

def test_worst_professor_query():
    response = client.post("/search_professors", json={"query": "Who is the worst professor in Math?"})
    assert response.status_code == 200
    assert "Worst professor in" in response.json()["response"]

def test_list_professors():
    response = client.post("/search_professors", json={"query": "List professors in the English department"})
    assert response.status_code == 200
    assert "professors in the" in response.json()["response"]

def test_professor_name_query():
    response = client.post("/search_professors", json={"query": "Tell me about Professor Erica Doran"})
    assert response.status_code == 200
    assert "Professor" in response.json()["response"] or "Multiple professors found" in response.json()["response"]
