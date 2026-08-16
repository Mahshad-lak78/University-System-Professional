"""Compatibility command for initializing the versioned database schema."""

from core.database import initialize_database


if __name__ == "__main__":
    initialize_database()
    print("University Management System database is ready.")
