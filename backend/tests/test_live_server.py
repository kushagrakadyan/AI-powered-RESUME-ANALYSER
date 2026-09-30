import io
import requests

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing GET /api/health...")
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check endpoint works!")
    print(f"  Response: {data}\n")

def test_unsupported_file():
    print("Testing POST /api/analyze with unsupported file type...")
    # Create a dummy .jpg file in memory
    files = {"file": ("resume.jpg", b"fake-image-bytes", "image/jpeg")}
    response = requests.post(f"{BASE_URL}/api/analyze", files=files)
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = response.json()
    assert "Unsupported file format" in data["detail"]
    print("✓ Correctly rejected unsupported file type!")
    print(f"  Response detail: {data['detail']}\n")

def test_missing_api_key():
    print("Testing POST /api/analyze with missing API key...")
    # Create a dummy .txt resume in memory
    resume_text = "John Doe\nSoftware Engineer\nPython, JavaScript, React\n5 years experience"
    files = {"file": ("resume.txt", io.BytesIO(resume_text.encode("utf-8")), "text/plain")}
    response = requests.post(f"{BASE_URL}/api/analyze", files=files)
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = response.json()
    assert "Gemini API key is not configured" in data["detail"]
    print("✓ Correctly returned 400 when Gemini API key is missing!")
    print(f"  Response detail: {data['detail']}\n")

if __name__ == "__main__":
    print("=== RUNNING LIVE API SERVER TESTS ===\n")
    try:
        test_health()
        test_unsupported_file()
        test_missing_api_key()
        print("=== ALL SERVER TESTS PASSED SUCCESSFULLY! ===")
    except AssertionError as ae:
        print(f"Assertion failed: {ae}")
    except Exception as e:
        print(f"Unexpected connection or test error: {e}")