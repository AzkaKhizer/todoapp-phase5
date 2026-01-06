"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestRegister:
    """Tests for POST /api/auth/register."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert "id" in data["user"]
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: User
    ):
        """Test registration fails with duplicate email."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "anotherpass123",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration fails with invalid email format."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepass123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration fails with short password."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login fails with wrong password."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login fails for non-existent user."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == 401


class TestGetMe:
    """Tests for GET /api/auth/me."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(
        self, client: AsyncClient, test_user: User, auth_headers: dict[str, str]
    ):
        """Test getting current user info when authenticated."""
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert str(data["id"]) == str(test_user.id)

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """Test getting current user info without authentication."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test getting current user info with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout."""

    @pytest.mark.asyncio
    async def test_logout_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test successful logout."""
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_unauthenticated(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401
