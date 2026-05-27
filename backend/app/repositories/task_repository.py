from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task, TaskStatus


class TaskRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        task: Task,
    ) -> Task:
        session.add(task)

        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        task_id,
    ) -> Task | None:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def update_status(
        session: AsyncSession,
        task: Task,
        status: TaskStatus,
    ) -> Task:
        task.status = status

        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def delete(
        session: AsyncSession,
        task: Task,
    ) -> None:
        await session.delete(task)
        await session.commit()