from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.result import Result


class ResultRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        result_obj: Result,
    ) -> Result:
        session.add(result_obj)

        await session.commit()
        await session.refresh(result_obj)

        return result_obj

    @staticmethod
    async def get_by_task_id(
        session: AsyncSession,
        task_id,
    ) -> Result | None:
        result = await session.execute(
            select(Result).where(Result.task_id == task_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        result_id,
    ) -> Result | None:
        result = await session.execute(
            select(Result).where(Result.id == result_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def delete(
        session: AsyncSession,
        result_obj: Result,
    ) -> None:
        await session.delete(result_obj)
        await session.commit()