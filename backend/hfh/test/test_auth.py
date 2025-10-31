import json
import os
from unittest.mock import patch

import pytest


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    # Set environment before importing app/db modules
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # Import controllers to register routes
    import hfh.controllers  # noqa: F401

    # Import models to ensure they are registered with SQLAlchemy
    import hfh.models.all  # noqa: F401
    from hfh.app import APP
    from hfh.db import DB

    APP.config["TESTING"] = True
    APP.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with APP.app_context():
        DB.create_all()
        yield APP
        DB.session.remove()
        DB.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    from hfh.db import DB
    from hfh.models.user import User
    from hfh.services.auth_service import AuthService

    user = User(name="testuser")
    AuthService.set_user_password(user, "testpassword")
    DB.session.add(user)
    DB.session.commit()
    return user


class TestLogin:
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/login",
            data=json.dumps({"username": "testuser", "password": "testpassword"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["username"] == "testuser"
        assert "id" in data

        # Check that session cookie is set
        assert "h4h_session" in response.headers.get("Set-Cookie", "")

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/login",
            data=json.dumps({"username": "testuser", "password": "wrongpassword"}),
            content_type="application/json",
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_login_missing_username(self, client):
        """Test login with missing username"""
        response = client.post(
            "/api/login",
            data=json.dumps({"password": "testpassword"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_login_missing_password(self, client):
        """Test login with missing password"""
        response = client.post(
            "/api/login",
            data=json.dumps({"username": "testuser"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_login_no_json_body(self, client):
        """Test login with no JSON body"""
        response = client.post("/api/login", data="", content_type="application/json")

        # Flask returns 400 when it can't parse JSON
        assert response.status_code == 400

    def test_login_sets_httponly_cookie(self, client, test_user):
        """Test that login sets HttpOnly cookie"""
        response = client.post(
            "/api/login",
            data=json.dumps({"username": "testuser", "password": "testpassword"}),
            content_type="application/json",
        )

        cookie_header = response.headers.get("Set-Cookie", "")
        assert "HttpOnly" in cookie_header
        assert "h4h_session=" in cookie_header

    def test_login_sets_secure_cookie_in_production(self, client, test_user):
        """Test that login sets Secure cookie in production"""
        with patch.dict(os.environ, {"FLASK_ENV": "production"}):
            response = client.post(
                "/api/login",
                data=json.dumps({"username": "testuser", "password": "testpassword"}),
                content_type="application/json",
            )

            cookie_header = response.headers.get("Set-Cookie", "")
            assert "Secure" in cookie_header


class TestLogout:
    def test_logout_success(self, client, test_user):
        """Test successful logout"""
        # First login to get a session
        login_response = client.post(
            "/api/login",
            data=json.dumps({"username": "testuser", "password": "testpassword"}),
            content_type="application/json",
        )
        assert login_response.status_code == 200

        # Extract session cookie
        cookie = None
        for header_name, header_value in login_response.headers:
            if header_name.lower() == "set-cookie" and "h4h_session=" in header_value:
                cookie = header_value.split(";")[0]
                break

        # Now logout
        logout_response = client.post("/api/logout", headers={"Cookie": cookie})

        assert logout_response.status_code == 200
        data = json.loads(logout_response.data)
        assert "message" in data

        # Check that cookie is cleared
        cookie_header = logout_response.headers.get("Set-Cookie", "")
        assert "h4h_session=" in cookie_header
        assert "Max-Age=0" in cookie_header

    def test_logout_not_authenticated(self, client):
        """Test logout when not authenticated"""
        response = client.post("/api/logout")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_logout_with_bearer_token(self, client, test_user):
        """Test logout with Authorization Bearer token"""
        # First login to get a session
        login_response = client.post(
            "/api/login",
            data=json.dumps({"username": "testuser", "password": "testpassword"}),
            content_type="application/json",
        )
        # Extract session_id from cookie
        session_id = None
        for header_name, header_value in login_response.headers:
            if header_name.lower() == "set-cookie" and "h4h_session=" in header_value:
                session_id = header_value.split("h4h_session=")[1].split(";")[0]
                break

        # Logout with Bearer token
        logout_response = client.post(
            "/api/logout", headers={"Authorization": f"Bearer {session_id}"}
        )

        assert logout_response.status_code == 200


class TestAuthService:
    def test_password_hashing(self, app):
        """Test password hashing"""
        from hfh.models.user import User
        from hfh.services.auth_service import AuthService

        user = User(name="testuser2")
        AuthService.set_user_password(user, "mypassword")

        assert user.password_hash != "mypassword"
        assert AuthService.verify_password("mypassword", user.password_hash) is True
        assert AuthService.verify_password("wrongpassword", user.password_hash) is False

    def test_user_authenticate(self, app, test_user):
        """Test user authentication"""
        from hfh.services.auth_service import AuthService

        user = AuthService.authenticate_user("testuser", "testpassword")
        assert user is not None
        assert user.name == "testuser"

        user = AuthService.authenticate_user("testuser", "wrongpassword")
        assert user is None

        user = AuthService.authenticate_user("nonexistent", "password")
        assert user is None


class TestSessionService:
    def test_create_session(self, app, test_user):
        """Test session creation"""
        from hfh.services.auth_service import AuthService

        session = AuthService.create_session(
            test_user, user_agent="TestAgent", ip_address="127.0.0.1"
        )

        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.user_agent == "TestAgent"
        assert session.ip_address == "127.0.0.1"
        assert session.created_at is not None
        assert session.last_used_at is not None

    def test_get_session_by_id(self, app, test_user):
        """Test getting session by ID"""
        from hfh.services.auth_service import AuthService

        session = AuthService.create_session(test_user)
        retrieved = AuthService.get_session_by_id(session.id)

        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.user_id == test_user.id

    def test_update_last_used(self, app, test_user):
        """Test updating last_used_at timestamp"""
        import time

        from hfh.services.auth_service import AuthService

        session = AuthService.create_session(test_user)
        original_time = session.last_used_at

        # Wait a bit and update
        time.sleep(0.1)
        AuthService.update_session_last_used(session)

        assert session.last_used_at > original_time

    def test_delete_session(self, app, test_user):
        """Test deleting a session"""
        from hfh.services.auth_service import AuthService

        session = AuthService.create_session(test_user)
        session_id = session.id

        AuthService.delete_session(session)

        retrieved = AuthService.get_session_by_id(session_id)
        assert retrieved is None
