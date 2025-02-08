from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Tag
from .decorators import session_manager


class Misc:
    @session_manager
    async def deserialize_tags(self, tags_string: str, session: AsyncSession = None) -> list[Tag]:
        tag_names = [tag_name.strip() for tag_name in tags_string.strip().split(" ")]

        select_stmt = (
            select(Tag)
            .where(Tag.name.in_(tag_names))
        )

        return list((await session.scalars(select_stmt)).all())
