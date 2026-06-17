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

def test_blueprints_analyze():
    import os
    if os.path.exists("analysis.txt"):
        try:
            os.remove("analysis.txt")
        except Exception:
            pass

    response = client.get("/blueprints/analyze")
    assert response.status_code == 200
    data = response.json()
    assert "bestBlueprint" in data
    assert "blueprints" in data
    assert data["bestBlueprint"] == "2"
    assert len(data["blueprints"]) == 2
    assert data["blueprints"][0]["id"] == "1"
    assert data["blueprints"][0]["quality"] == 3
    assert data["blueprints"][1]["id"] == "2"
    assert data["blueprints"][1]["quality"] == 6

    # Verify analysis.txt exists and contains proper text
    assert os.path.exists("analysis.txt")
    with open("analysis.txt", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Blueprint 1: 3" in content
    assert "Blueprint 2: 6" in content
    assert "Best blueprint is the blueprint 2." in content

def test_blueprints_analyze_missing_file():
    import os
    seed_exists = os.path.exists("seed.txt")
    if seed_exists:
        os.rename("seed.txt", "seed.txt.bak")
    try:
        response = client.get("/blueprints/analyze")
        assert response.status_code == 400
        assert "Blueprint file 'seed.txt' not found" in response.json()["detail"]
    finally:
        if seed_exists:
            os.rename("seed.txt.bak", "seed.txt")

def test_blueprints_analyze_empty_file():
    import os
    seed_exists = os.path.exists("seed.txt")
    original_content = ""
    if seed_exists:
        with open("seed.txt", "r", encoding="utf-8") as f:
            original_content = f.read()
    
    with open("seed.txt", "w", encoding="utf-8") as f:
        f.write("")
        
    try:
        response = client.get("/blueprints/analyze")
        assert response.status_code == 400
        assert "The blueprint file is empty." in response.json()["detail"]
    finally:
        if seed_exists:
            with open("seed.txt", "w", encoding="utf-8") as f:
                f.write(original_content)
        else:
            try:
                os.remove("seed.txt")
            except Exception:
                pass

def test_blueprints_analyze_malformed_file():
    import os
    seed_exists = os.path.exists("seed.txt")
    original_content = ""
    if seed_exists:
        with open("seed.txt", "r", encoding="utf-8") as f:
            original_content = f.read()
            
    with open("seed.txt", "w", encoding="utf-8") as f:
        f.write("Blueprint 1: 4 2 3 14 2 7 1 5\nBlueprint 2: 2 3 3 8 3 12 2 4 4 4\n")
        
    try:
        response = client.get("/blueprints/analyze")
        assert response.status_code == 400
        assert "Error parsing blueprint line 1" in response.json()["detail"]
    finally:
        if seed_exists:
            with open("seed.txt", "w", encoding="utf-8") as f:
                f.write(original_content)
        else:
            try:
                os.remove("seed.txt")
            except Exception:
                pass

def test_serve_frontend():
    response = client.get("/")
    assert response.status_code in (200, 404)

def test_upload_no_file():
    response = client.post("/upload")
    assert response.status_code == 422



