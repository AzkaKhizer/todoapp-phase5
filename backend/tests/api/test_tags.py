"""API tests for tag endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tag


@pytest_asyncio.fixture
async def sample_tag(async_session: AsyncSession, test_user) -> Tag:
    """Create a sample tag for testing."""
    tag = Tag(
        id=uuid.uuid4(),
        name="work",
        color="#3B82F6",
        user_id=str(test_user.id),
    )
    async_session.add(tag)
    await async_session.commit()
    await async_session.refresh(tag)
    return tag


@pytest_asyncio.fixture
async def multiple_tags(async_session: AsyncSession, test_user) -> list[Tag]:
    """Create multiple tags for testing."""
    tags_data = [
        {"name": "work", "color": "#3B82F6"},
        {"name": "personal", "color": "#10B981"},
        {"name": "urgent", "color": "#EF4444"},
    ]

    tags = []
    for data in tags_data:
        tag = Tag(
            id=uuid.uuid4(),
            user_id=str(test_user.id),
            **data,
        )
        async_session.add(tag)
        tags.append(tag)

    await async_session.commit()
    for tag in tags:
        await async_session.refresh(tag)

    return tags


class TestTagEndpoints:
    """Test tag CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_tags_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test listing tags when none exist."""
        response = await client.get("/api/tags", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_list_tags_with_data(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        multiple_tags: list[Tag],
    ):
        """Test listing tags with existing data."""
        response = await client.get("/api/tags", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3

        # Verify tag structure
        tag = data["data"][0]
        assert "id" in tag
        assert "name" in tag
        assert "color" in tag
        assert "task_count" in tag

    @pytest.mark.asyncio
    async def test_create_tag(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test creating a new tag."""
        payload = {"name": "new-tag", "color": "#FF5733"}

        response = await client.post(
            "/api/tags", json=payload, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new-tag"
        assert data["color"] == "#FF5733"
        assert data["task_count"] == 0
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_tag_without_color(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test creating a tag without color."""
        payload = {"name": "no-color-tag"}

        response = await client.post(
            "/api/tags", json=payload, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "no-color-tag"
        assert data["color"] is None

    @pytest.mark.asyncio
    async def test_create_duplicate_tag(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        sample_tag: Tag,
    ):
        """Test creating a tag with duplicate name fails."""
        payload = {"name": sample_tag.name, "color": "#000000"}

        response = await client.post(
            "/api/tags", json=payload, headers=auth_headers
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_tag_invalid_color(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test creating a tag with invalid color format."""
        payload = {"name": "invalid-color", "color": "not-a-color"}

        response = await client.post(
            "/api/tags", json=payload, headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_delete_tag(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        sample_tag: Tag,
    ):
        """Test deleting a tag."""
        response = await client.delete(
            f"/api/tags/{sample_tag.id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify tag is deleted
        list_response = await client.get("/api/tags", headers=auth_headers)
        tags = list_response.json()["data"]
        assert not any(t["id"] == str(sample_tag.id) for t in tags)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tag(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test deleting a tag that doesn't exist."""
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/api/tags/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404


class TestTagIsolation:
    """Test that tags are properly isolated between users."""

    @pytest.mark.asyncio
    async def test_cannot_see_other_user_tags(
        self,
        client: AsyncClient,
        other_auth_headers: dict[str, str],
        sample_tag: Tag,
    ):
        """Test that users cannot see other users' tags."""
        response = await client.get("/api/tags", headers=other_auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Other user should not see sample_tag
        assert not any(t["id"] == str(sample_tag.id) for t in data["data"])

    @pytest.mark.asyncio
    async def test_cannot_delete_other_user_tag(
        self,
        client: AsyncClient,
        other_auth_headers: dict[str, str],
        sample_tag: Tag,
    ):
        """Test that users cannot delete other users' tags."""
        response = await client.delete(
            f"/api/tags/{sample_tag.id}", headers=other_auth_headers
        )

        # Should return 404 (not found for this user)
        assert response.status_code == 404


class TestTagAuthentication:
    """Test tag endpoint authentication."""

    @pytest.mark.asyncio
    async def test_list_tags_unauthenticated(self, client: AsyncClient):
        """Test listing tags without authentication."""
        response = await client.get("/api/tags")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_tag_unauthenticated(self, client: AsyncClient):
        """Test creating a tag without authentication."""
        payload = {"name": "test", "color": "#000000"}
        response = await client.post("/api/tags", json=payload)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_tag_unauthenticated(self, client: AsyncClient):
        """Test deleting a tag without authentication."""
        fake_id = uuid.uuid4()
        response = await client.delete(f"/api/tags/{fake_id}")
        assert response.status_code == 401
