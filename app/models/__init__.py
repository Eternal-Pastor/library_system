from app.models.base import Base

# Импорт моделей для регистрации в metadata
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.group import Group, UserGroup

__all__ = [
    "Base",
    "User",
    "Role",
    "UserRole",
    "Group",
    "UserGroup",
]
