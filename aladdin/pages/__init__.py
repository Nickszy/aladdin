from .about import about
from .index import index
from .profile import profile
from .settings import settings
from .table import table
from .pdf import pdf
from .chat import chat

from .antdchat import chatx
from .management import management

# from .news import new
from .news import feeds_page, feed_page, author_page

# from .feishu import feishudoc

__all__ = [
    "about",
    "index",
    "profile",
    "settings",
    "table",
    "pdf",
    "chat",
    "chatx",
    "management",
]
