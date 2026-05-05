import re
import uuid
import hashlib
import bcrypt
import argon2.low_level as argon2
from uuid_extensions import uuid7
import uuid6
from storage.config_store import get_setting

HASH_METHODS = {
    "bcrypt": lambda pwd: bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode(),
    "argon2": lambda pwd: argon2.hash_secret_raw(
        pwd.encode(), argon2.random_salt(16),
        time_cost=2, memory_cost=65536, parallelism=2,
        hash_len=32, type=argon2.Type.ID
    ).hex(),
    "sha256": lambda pwd: hashlib.sha256(pwd.encode()).hexdigest(),
}

UUID_GENERATORS = {
    "uuid7": lambda: str(uuid7()),
    "uuid6": lambda: str(uuid6()),
    "uuid5": lambda: str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid7()))),
}

class SQLReplacer:
    def __init__(self, sql: str):
        self.sql = sql

    def replace_uuids(self, uuid_method: str = "uuid7") -> "SQLReplacer":
        generator = UUID_GENERATORS.get(uuid_method, UUID_GENERATORS["uuid7"])
        placeholders = set(re.findall(r'uuid\d+', self.sql))
        mapping = {p: generator() for p in placeholders}
        for placeholder, real_uuid in mapping.items():
            self.sql = self.sql.replace(placeholder, real_uuid)
        return self

    def replace_passwords(self, hash_method: str = None) -> "SQLReplacer":
        hash_method = hash_method or get_setting("hash_method", "bcrypt")
        if hash_method not in HASH_METHODS:
            raise ValueError(f"Méthode inconnue: {hash_method}. Disponibles: {list(HASH_METHODS.keys())}")
        hasher = HASH_METHODS[hash_method]
        password = get_setting("password", "Password123!")
        hashed = hasher(password)
        placeholders = set(re.findall(r'\{password\}', self.sql))
        for placeholder in placeholders:
            self.sql = self.sql.replace(placeholder, f"{hashed}")
        return self

    def get(self) -> str:
        return self.sql
