import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_dir: Path
    database_path: Path
    session_secret: str


def get_settings() -> Settings:
    project_dir = Path(__file__).resolve().parents[1]
    return Settings(
        project_dir=project_dir,
        database_path=Path(os.environ.get("UNIVERSITY_DB_PATH", project_dir / "university.db")),
        session_secret=os.environ.get("SESSION_SECRET", "development-only-change-this-before-deployment"),
    )
