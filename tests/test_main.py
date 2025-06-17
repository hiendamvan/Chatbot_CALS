from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

def test_classify():
    # Test 1:
    response = client.post("/classify", json={
        "question": "What units are involved in implementing the strategy and who oversees them?",
        "history": []
    })
    assert response.status_code == 200
    assert response.json() == {"category": "multi-hop"}

    # Test 2:
    response = client.post("/classify", json={
        "question": "Hello, how are you?",
        "history": []
    })
    assert response.status_code == 200
    assert response.json() == {"category": "greeting"}

    # Test 3: 
    response = client.post("/classify", json={
        "question": "What is the capital of France?",
        "history": []
    })
    assert response.status_code == 200
    assert response.json() == {"category": "simple"}