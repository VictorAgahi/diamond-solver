from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_upload_seed_file():
    file_content = "Blueprint 1: 4 2 3 14 2 7 1 5 3\nBlueprint 2: 2 3 3 8 3 12 2 4 4"
    response = client.post(
        "/upload",
        files={"file": ("seed.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "part1" in data
    assert "part2" in data

def test_upload_invalid_file_type():
    response = client.post(
        "/upload",
        files={"file": ("image.png", "fake image data", "image/png")}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file type. Only .txt files are allowed."}

def test_upload_empty_file():
    response = client.post(
        "/upload",
        files={"file": ("empty.txt", "", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The uploaded file is empty."}

def test_upload_malformed_file():
    file_content = "Blueprint 1: 4 2 3 14 2 7 1 5\nBlueprint 2: 2 3 3 8 3 12 2 4 4 4"
    response = client.post(
        "/upload",
        files={"file": ("bad_seed.txt", file_content, "text/plain")}
    )
    assert response.status_code == 400
    assert "Error parsing line 1: Expected 10 integers" in response.json()["detail"]
