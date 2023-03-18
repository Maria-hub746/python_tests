from unittest.mock import MagicMock, patch
import pytest
from src.services.messages import NOT_FOUND
from src.services.urls_const import URL_SIGNUP, URL_LOGIN
from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post(URL_SIGNUP, json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(URL_LOGIN,
                           data={"username": user.get('email'), "password": user.get('password')},
                           )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {
            "name": 'Test',
            "surname": 'Test',
            "email": 'test@gmail.com',
            "phone": "093 082-76-37",
        }
        response = client.post("/api/contacts/create", json=contact,  headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["name"] == contact["name"]
        assert data["surname"] == contact["surname"]
        assert data["email"] == contact["email"]
        assert data["phone"] == contact["phone"]
        assert "id" in data


def test_get_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == 'Test'
        assert data["surname"] == 'Test'


def test_get_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_contacts(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["name"] == 'Test'


def test_update_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {
            "name": 'User',
            "surname": 'Test',
            "email": 'test@gmail.com',
            "phone": "093 082-76-37",
        }
        response = client.put("/api/contacts/update/1", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["name"] == contact["name"]
        assert data["surname"] == contact["surname"]
        assert data["email"] == contact["email"]
        assert data["phone"] == contact["phone"]


def test_update_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        contact = {
            "name": 'User',
            "surname": 'Test',
            "email": 'test@gmail.com',
            "phone": "093 082-76-37",
        }
        response = client.put("/api/contacts/update/3", json=contact, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND

def test_get_birthdays(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/contacts/bday", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert type(data) == list

def test_remove_contact(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete("/api/contacts/delete/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204, response.text

def test_remove_contact_not_found(client, token):
    with patch.object(auth_service, 'auth_redis') as r_mock:
        r_mock.get.return_value = None
        response = client.delete("/api/contacts/delete/2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND