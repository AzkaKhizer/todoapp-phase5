"""Tests for multi-user task isolation."""

import pytest
from httpx import AsyncClient

from app.models.task import Task
from app.models.user import User


class TestUserIsolation:
    """Tests to ensure tasks are properly isolated between users."""

    @pytest.mark.asyncio
    async def test_user_cannot_see_other_user_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_user: User,
        other_user_task: Task,
    ):
        """Test that user cannot see tasks belonging to other users."""
        response = await client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Should not see other user's task
        task_ids = [t["id"] for t in data["tasks"]]
        assert str(other_user_task.id) not in task_ids

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_task_directly(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_user_task: Task,
    ):
        """Test that user cannot access other user's task by ID."""
        response = await client.get(
            f"/api/tasks/{other_user_task.id}", headers=auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_cannot_update_other_user_task(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_user_task: Task,
    ):
        """Test that user cannot update other user's task."""
        response = await client.put(
            f"/api/tasks/{other_user_task.id}",
            json={"title": "Hacked", "description": "Malicious update"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_cannot_patch_other_user_task(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_user_task: Task,
    ):
        """Test that user cannot patch other user's task."""
        response = await client.patch(
            f"/api/tasks/{other_user_task.id}",
            json={"title": "Hacked"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_cannot_delete_other_user_task(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_user_task: Task,
    ):
        """Test that user cannot delete other user's task."""
        response = await client.delete(
            f"/api/tasks/{other_user_task.id}", headers=auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_cannot_toggle_other_user_task(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_user_task: Task,
    ):
        """Test that user cannot toggle other user's task."""
        response = await client.patch(
            f"/api/tasks/{other_user_task.id}/toggle", headers=auth_headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_each_user_sees_only_their_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_auth_headers: dict[str, str],
        test_task: Task,
        other_user_task: Task,
    ):
        """Test that each user sees only their own tasks."""
        # First user's view
        response1 = await client.get("/api/tasks", headers=auth_headers)
        assert response1.status_code == 200
        data1 = response1.json()
        task_ids1 = [t["id"] for t in data1["tasks"]]
        assert str(test_task.id) in task_ids1
        assert str(other_user_task.id) not in task_ids1

        # Second user's view
        response2 = await client.get("/api/tasks", headers=other_auth_headers)
        assert response2.status_code == 200
        data2 = response2.json()
        task_ids2 = [t["id"] for t in data2["tasks"]]
        assert str(other_user_task.id) in task_ids2
        assert str(test_task.id) not in task_ids2

    @pytest.mark.asyncio
    async def test_task_creation_assigns_to_correct_user(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        other_auth_headers: dict[str, str],
    ):
        """Test that created tasks are assigned to the authenticated user."""
        # User 1 creates a task
        response1 = await client.post(
            "/api/tasks",
            json={"title": "User 1 Task"},
            headers=auth_headers,
        )
        assert response1.status_code == 201
        task_id = response1.json()["id"]

        # User 1 can access it
        response = await client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200

        # User 2 cannot access it
        response = await client.get(f"/api/tasks/{task_id}", headers=other_auth_headers)
        assert response.status_code == 403
