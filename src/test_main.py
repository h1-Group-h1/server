from fastapi.testclient import TestClient
from main import app

#from unittest import *

client = TestClient(app)

def test_response

#class TestMain(TestCase):
print("Testing root")
response = client.get('/')
assert response.json() == {"Hello": "World"}, "Wrong root response"

print("Testing users")
response = client.post('/add_user', {"email": "test_email1", "name": "test1", "password": "tp1"})
print(response.status_code)
assert response.status_code == 200
assert response.json()["email"] == "test_email1"
assert response.json()["id"] == 1
assert response.json()["name"] == "test1"
assert response.json()["password"] != "tp1"
