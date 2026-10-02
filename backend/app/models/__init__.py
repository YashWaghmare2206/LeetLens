"""Models package — import all models so Alembic/Base.metadata sees them."""
from app.models.user import User  # noqa: F401
from app.models.problem import (  # noqa: F401
    Problem, Topic, Pattern,
    ProblemTopic, ProblemPattern,
    UserSolvedProblem,
    Difficulty, ClassificationSource, ClassificationStatus,
)
from app.models.sync_job import SyncJob, SyncStatus  # noqa: F401
