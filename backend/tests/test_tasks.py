"""Tests for task endpoints."""

import uuid

import pytest
from httpx import AsyncClient

from app.models.task import Task
from app.models.user import User


class TestListTasks:
    """Tests for GET /api/tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test listing tasks when user has none."""
        response = await client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_task: Task,
        completed_task: Task,
    ):
        """Test listing tasks returns user's tasks."""
        response = await client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_task: Task,
        completed_task: Task,
    ):
        """Test pagination parameters work correctly."""
        response = await client.get(
            "/api/tasks?limit=1&offset=0", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["total"] == 2
        assert data["limit"] == 1
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_unauthenticated(self, client: AsyncClient):
        """Test listing tasks without authentication."""
        response = await client.get("/api/tasks")
        assert response.status_code == 401


class TestCreateTask:
    """Tests for POST /api/tasks."""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test successful task creation."""
        response = await client.post(
            "/api/tasks",
            json={
                "title": "New Task",
                "description": "Task description",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["is_complete"] is False
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_task_minimal(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test task creation with minimal data."""
        response = await client.post(
            "/api/tasks",
            json={
                "title": "Minimal Task",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] == ""

    @pytest.mark.asyncio
    async def test_create_task_empty_title(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test task creation fails with empty title."""
        response = await client.post(
            "/api/tasks",
            json={
                "title": "",
                "description": "Some description",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_unauthenticated(self, client: AsyncClient):
        """Test task creation without authentication."""
        response = await client.post(
            "/api/tasks",
            json={
                "title": "New Task",
            },
        )
        assert response.status_code == 401


class TestGetTask:
    """Tests for GET /api/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_get_task_success(
        self, client: AsyncClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Test getting a single task."""
        response = await client.get(
            f"/api/tasks/{test_task.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_task.id)
        assert data["title"] == test_task.title

    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test getting a non-existent task."""
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/tasks/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_unauthenticated(
        self, client: AsyncClient, test_task: Task
    ):
        """Test getting a task without authentication."""
        response = await client.get(f"/api/tasks/{test_task.id}")
        assert response.status_code == 401


class TestUpdateTask:
    """Tests for PUT /api/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_update_task_success(
        self, client: AsyncClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Test successful task update."""
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={
                "title": "Updated Title",
                "description": "Updated Description",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"

    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test updating a non-existent task."""
        fake_id = uuid.uuid4()
        response = await client.put(
            f"/api/tasks/{fake_id}",
            json={
                "title": "Updated Title",
                "description": "Updated Description",
            },
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestPatchTask:
    """Tests for PATCH /api/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_patch_task_title_only(
        self, client: AsyncClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Test partial update with title only."""
        response = await client.patch(
            f"/api/tasks/{test_task.id}",
            json={"title": "Patched Title"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Patched Title"
        assert data["description"] == test_task.description

    @pytest.mark.asyncio
    async def test_patch_task_is_complete(
        self, client: AsyncClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Test partial update with is_complete."""
        response = await client.patch(
            f"/api/tasks/{test_task.id}",
            json={"is_complete": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is True


class TestDeleteTask:
    """Tests for DELETE /api/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self, client: AsyncClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Test successful task deletion."""
        response = await client.delete(
            f"/api/tasks/{test_task.id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify task is gone
        response = await client.get(
            f"/api/tasks/{test_task.id}", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test deleting a non-existent task."""
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/api/tasks/{fake_id}", headers=auth_headers
        )
        assert response.status_code == 404


class TestToggleTask:
    """Tests for PATCH /api/tasks/{task_id}/toggle."""

    @pytest.mark.asyncio
    async def test_toggle_incomplete_to_complete(
        self, client: AsyncClient, auth_headers: dict[str, str], test_task: Task
    ):
        """Test toggling incomplete task to complete."""
        assert test_task.is_complete is False

        response = await client.patch(
            f"/api/tasks/{test_task.id}/toggle", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is True

    @pytest.mark.asyncio
    async def test_toggle_complete_to_incomplete(
        self, client: AsyncClient, auth_headers: dict[str, str], completed_task: Task
    ):
        """Test toggling complete task to incomplete."""
        assert completed_task.is_complete is True

        response = await client.patch(
            f"/api/tasks/{completed_task.id}/toggle", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is False

    @pytest.mark.asyncio
    async def test_toggle_task_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ):
        """Test toggling a non-existent task."""
        fake_id = uuid.uuid4()
        response = await client.patch(
            f"/api/tasks/{fake_id}/toggle", headers=auth_headers
        )
        assert response.status_code == 404
