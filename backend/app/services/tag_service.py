"""Tag service for CRUD operations on tags."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tag


class TagService:
    """Service for managing user tags."""

    def __init__(self, session: AsyncSession):
        """Initialize tag service.

        Args:
            session: Async database session
        """
        self.session = session

    async def get_tags(self, user_id: str) -> list[Tag]:
        """Get all tags for a user.

        Args:
            user_id: User ID

        Returns:
            List of user's tags
        """
        result = await self.session.execute(
            select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
        )
        return list(result.scalars().all())

    async def get_tag_by_id(self, tag_id: uuid.UUID, user_id: str) -> Tag | None:
        """Get a tag by ID.

        Args:
            tag_id: Tag ID
            user_id: User ID (for ownership check)

        Returns:
            Tag if found and owned by user, None otherwise
        """
        result = await self.session.execute(
            select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_tag_by_name(self, name: str, user_id: str) -> Tag | None:
        """Get a tag by name.

        Args:
            name: Tag name
            user_id: User ID

        Returns:
            Tag if found, None otherwise
        """
        result = await self.session.execute(
            select(Tag).where(Tag.name == name, Tag.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_tag(
        self,
        name: str,
        user_id: str,
        color: str | None = None,
    ) -> Tag:
        """Create a new tag.

        Args:
            name: Tag name
            user_id: User ID
            color: Optional hex color code

        Returns:
            Created tag
        """
        tag = Tag(name=name, user_id=user_id, color=color)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def get_or_create_tag(
        self,
        name: str,
        user_id: str,
        color: str | None = None,
    ) -> Tag:
        """Get an existing tag or create a new one.

        Args:
            name: Tag name
            user_id: User ID
            color: Optional hex color code (only used for new tags)

        Returns:
            Existing or newly created tag
        """
        existing = await self.get_tag_by_name(name, user_id)
        if existing:
            return existing
        return await self.create_tag(name, user_id, color)

    async def update_tag(
        self,
        tag_id: uuid.UUID,
        user_id: str,
        name: str | None = None,
        color: str | None = None,
    ) -> Tag | None:
        """Update a tag.

        Args:
            tag_id: Tag ID
            user_id: User ID (for ownership check)
            name: New tag name
            color: New hex color code

        Returns:
            Updated tag if found, None otherwise
        """
        tag = await self.get_tag_by_id(tag_id, user_id)
        if not tag:
            return None

        if name is not None:
            tag.name = name
        if color is not None:
            tag.color = color

        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def delete_tag(self, tag_id: uuid.UUID, user_id: str) -> bool:
        """Delete a tag.

        Args:
            tag_id: Tag ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        tag = await self.get_tag_by_id(tag_id, user_id)
        if not tag:
            return False

        await self.session.delete(tag)
        await self.session.commit()
        return True

    async def get_tags_by_names(self, names: list[str], user_id: str) -> list[Tag]:
        """Get tags by names, creating any that don't exist.

        Args:
            names: List of tag names
            user_id: User ID

        Returns:
            List of tags (existing or newly created)
        """
        tags = []
        for name in names:
            tag = await self.get_or_create_tag(name, user_id)
            tags.append(tag)
        return tags
