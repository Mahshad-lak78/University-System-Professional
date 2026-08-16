import unittest
from types import SimpleNamespace

from core.dependencies import require_roles
from core.security import hash_password, verify_password
from fastapi import HTTPException
from services.auth_service import authenticate
from tests.helpers import seed_student, temporary_database


class SecurityTests(unittest.TestCase):
    def test_password_hash_is_not_plaintext_and_verifies(self):
        encoded = hash_password("safe-password")
        self.assertNotEqual(encoded, "safe-password")
        self.assertTrue(verify_password("safe-password", encoded))
        self.assertFalse(verify_password("wrong-password", encoded))

    def test_authentication_and_student_role(self):
        with temporary_database():
            user_id, _ = seed_student()
            user = authenticate("student", "secret")
            self.assertEqual(user["id"], user_id)
            request = SimpleNamespace(session={"user_id": user_id})
            self.assertEqual(require_roles("student")(request)["role"], "student")
            with self.assertRaises(HTTPException) as denied:
                require_roles("admin")(request)
            self.assertEqual(denied.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
