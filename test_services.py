from core.security import hash_password, verify_password


encoded = hash_password("test-password")
assert verify_password("test-password", encoded)
assert not verify_password("wrong-password", encoded)
print("service smoke test passed")
