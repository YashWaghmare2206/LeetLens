"""Pydantic schemas for sync jobs."""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.sync_job import SyncStatus


class SyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: SyncStatus
    progress: int = 100
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    created_at: datetime | None = None


class SyncJobCreate(BaseModel):
    user_id: int
