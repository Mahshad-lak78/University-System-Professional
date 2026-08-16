"""Compatibility exports for the previous user service module."""

from services.auth_service import authenticate as login
from services.auth_service import register_student as create_student_account
from repositories.university_repository import get_student_by_user_id, get_user_by_id


__all__ = ["login", "create_student_account", "get_student_by_user_id", "get_user_by_id"]
