from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

from supabase import (
    create_client,
    Client,
    AsyncClient,
    create_async_client,
    acreate_client,
)


supabase: Client = create_client(url, key)


# supabase: AsyncClient = create_async_client(url, key)


# async def get_supabase_client():
#     supabase = await acreate_client(url, key)
#     return supabase


ali_url = os.environ.get("aliSUPABASE_URL")
ali_key = os.environ.get("aliSUPABASE_KEY")

_client: AsyncClient | None = None


async def get_supabase_client():
    global _client
    if _client is None:
        # _client = await acreate_client(ali_url, ali_key)
        _client = await acreate_client(url, key)
    return _client


# # 全局缓存 client
# _supabase: AsyncClient | None = None


# def get_supabase_client() -> AsyncClient:
#     """获取全局 Supabase AsyncClient（单例）"""
#     global _supabase
#     if _supabase is None:
#         _supabase = acreate_client(url, key)

#     return _supabase
