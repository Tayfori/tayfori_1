"""
AFAD Yönetim Sistemi - API Routes
"""
from backend.app.routes import (
    auth,
    users,
    disasters,
    victims,
    inventory,
    notifications,
    dashboard,
)

__all__ = [
    "auth",
    "users",
    "disasters",
    "victims",
    "inventory",
    "notifications",
    "dashboard",
]
