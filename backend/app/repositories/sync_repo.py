"""SyncJob repository."""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sync_job import SyncJob, SyncStatus


class SyncJobRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, user_id: int) -> SyncJob:
        job = SyncJob(user_id=user_id, status=SyncStatus.PENDING, progress=0)
        self._db.add(job)
        await self._db.flush()
        await self._db.refresh(job)
        return job

    async def get_by_id(self, job_id: int) -> SyncJob | None:
        result = await self._db.execute(select(SyncJob).where(SyncJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_latest_for_user(self, user_id: int) -> SyncJob | None:
        result = await self._db.execute(
            select(SyncJob)
            .where(SyncJob.user_id == user_id)
            .order_by(SyncJob.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def mark_running(self, job: SyncJob) -> SyncJob:
        job.status = SyncStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        self._db.add(job)
        await self._db.flush()
        return job

    async def set_progress(self, job: SyncJob, progress: int) -> SyncJob:
        job.progress = min(progress, 100)
        self._db.add(job)
        await self._db.flush()
        return job

    async def mark_success(self, job: SyncJob) -> SyncJob:
        job.status = SyncStatus.SUCCESS
        job.progress = 100
        job.completed_at = datetime.now(timezone.utc)
        self._db.add(job)
        await self._db.flush()
        return job

    async def mark_failed(self, job: SyncJob, error: str) -> SyncJob:
        job.status = SyncStatus.FAILED
        job.completed_at = datetime.now(timezone.utc)
        job.error = error
        self._db.add(job)
        await self._db.flush()
        return job
