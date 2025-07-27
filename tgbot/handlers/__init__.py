"""Import all routers and add them to routers_list."""
from tgbot.handlers.user.achievements import achievements_router
from .admin.main import admin_router
from tgbot.handlers.user.awards import awards_router
from tgbot.handlers.user.main import user_router
from .admin.search import search_router

routers_list = [
    admin_router,
    search_router,
    user_router,
    awards_router,
    achievements_router
]

__all__ = [
    "routers_list",
]
