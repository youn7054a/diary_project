import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from main import app, get_session, SQLModel, test_engine as engine

from sqlmodel import SQLModel, create_engine
import random
import string

client = TestClient(app)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # SQLModel.metadata.drop_all(engine)

# test user create
def test_create_user(session):
    random_email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@example.com"

    user_data = {
        "username": "testuser",
        "email": random_email,
        "password_hash": "securepassword"
    }

    # Send a POST request to the user creation endpoint
    response = client.post("/users", json=user_data)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 200

    # Assert that the response contains the expected data
    response_data = response.json()
    assert response_data["username"] == user_data["username"]
    assert response_data["email"] == user_data["email"]

