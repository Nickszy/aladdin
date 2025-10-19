import datetime
import json
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import reflex as rx
from fastapi import FastAPI, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Session

from aladdin.db import get_session, engine
from aladdin.services.supabase import get_supabase_client
from aladdin.services.ai_service import AIService
from aladdin.services.data_service import DataService
from aladdin.services.entry_service import EntryService
from aladdin.models.entry import Entry as db_Entry

from aladdin.models.feed import sql_Feed, Feed
from aladdin.services.tag_service import TaggingService
from aladdin.utils.logger import log_info, log_error, log_debug

# Create a FastAPI app
fastapi_app = FastAPI(title="aladdin")


# Add routes to the FastAPI app
@fastapi_app.get("/api/items")
async def get_items():
    log_info("get_items")
    return dict(items=["Item1", "Item2", "Item3"])


class Media(BaseModel):
    url: str
    type: str = Field(..., pattern=r"^(photo|video)$")  # ← 改这里
    preview_image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    blurhash: Optional[str] = None


class Entry(BaseModel):
    id: str
    publishedAt: datetime.datetime
    insertedAt: datetime.datetime
    feedId: str
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    guid: str
    media: Optional[List[Media]] = None


class Feed(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    url: str
    description: Optional[str] = None
    image: Optional[str] = None
    errorAt: Optional[datetime.datetime] = None
    siteUrl: str
    ownerUserId: Optional[str] = None
    errorMessage: Optional[str] = None
    lastModifiedHeader: Optional[str] = None
    etagHeader: Optional[str] = None
    checkedAt: datetime.datetime
    ttl: Optional[int] = None
    language: Optional[str] = None


class WebhookPayload(BaseModel):
    entry: Entry
    feed: Feed
    view: int


from lxml import html as lxml_html
import re


def remove_html_by_lxml(html_str):
    # 1. 解析HTML
    tree = lxml_html.fromstring(html_str)
    # 2. 提取所有文本（strip=True 去除首尾空格）
    clean_str = tree.xpath("string(.)").strip()
    # 3. 优化文本格式
    clean_str = re.sub(r"\s+", " ", clean_str)
    return clean_str


def to_postgrest_dict(model: SQLModel) -> dict:
    return json.loads(
        json.dumps(
            model.dict(exclude_none=True),
            default=lambda o: (
                o.isoformat() if isinstance(o, datetime.datetime) else str(o)
            ),
        )
    )


# # Create a Reflex app with the FastAPI app as the API transformer
# app = rx.App(api_transformer=fastapi_app)
@fastapi_app.post("/folo")
async def webhook_handler(
    request: Request, payload: WebhookPayload, session: Session = Depends(get_session)
):
    """
    接收 RSS 更新，转发到飞书群，并保存到数据库
    """
    # 保存到数据库
    # print(payload)
    try:
        # 保存feed
        db_feed = sql_Feed(
            id=payload.entry.feedId,
            url=payload.feed.url,
            siteUrl=payload.feed.siteUrl,
            lastModifiedHeader=payload.feed.lastModifiedHeader,
            etagHeader=payload.feed.etagHeader,
            errorMessage=payload.feed.errorMessage,
            errorAt=payload.feed.errorAt,
            image=payload.feed.image,
            description=payload.feed.description,
            title=payload.feed.title,
            checkedAt=payload.feed.checkedAt,
            ttl=payload.feed.ttl,
            ownerUserId=payload.feed.ownerUserId,
            language=payload.feed.language,
        )
        # 修改为await调用
        db_feed = await DataService(engine).upsert(db_feed, keys=("id",))
        log_info("数据库保存成功")

        # 保存feed
        feed = Feed(
            id=payload.entry.feedId,
            url=payload.feed.url,
            siteUrl=payload.feed.siteUrl,
            lastModifiedHeader=payload.feed.lastModifiedHeader,
            etagHeader=payload.feed.etagHeader,
            errorMessage=payload.feed.errorMessage,
            errorAt=payload.feed.errorAt,
            image=payload.feed.image,
            description=payload.feed.description,
            title=payload.feed.title,
            checkedAt=payload.feed.checkedAt,
            ttl=payload.feed.ttl,
            ownerUserId=payload.feed.ownerUserId,
            language=payload.feed.language,
        )
        row = to_postgrest_dict(db_feed)
        supabase = await get_supabase_client()
        response = await supabase.table("feed").upsert(feed.model_dump_json()).execute()

        log_info(f"subapase保存成功 {db_feed.title} {db_feed.url}")

        # 保存entry
        media_list = payload.entry.media or "[]"
        db_entry = db_Entry(
            id=payload.entry.id,
            title=payload.entry.title,
            url=payload.entry.url,
            content=payload.entry.content,
            description=payload.entry.description,
            guid=payload.entry.guid,
            author=payload.entry.author,
            publishedAt=payload.entry.publishedAt,
            insertedAt=payload.entry.insertedAt,
            feedId=payload.entry.feedId,
            media=media_list,
        )
        import json
        from datetime import datetime

        row = to_postgrest_dict(db_entry)
        response = await supabase.table("entry").upsert(row).execute()
        # 修改为await调用
        db_entry = await EntryService(session).upsert(db_entry, keys=("guid",))
        # print(db_entry)

        log_info(f"数据库保存成功 {db_entry.title} {db_entry.guid}")
        # ai = AIService(
        #     api_key="123456",
        #     base_url="http://100.64.0.2/e/l3m9vpgyzoq9vj9c",
        #     # api_key="123456",
        #     # base_url="https://u9ec3f0p2fj6vobt.ai-plugin.io",
        # )

        # 使用异步调用处理新条目
        # if db_entry.content and len(db_entry.content) > 100:
        #     # 修改为await调用
        #     await TaggingService(ai_service=ai, session=session).process_new_entry(
        #         entry=db_entry
        #     )

        # # 如果有媒体，也保存
        # if payload.entry.media:
        #     for media_item in payload.entry.media:
        #         db_media = DBMedia(
        #             url=media_item.url,
        #             type=media_item.type,
        #             preview_image_url=media_item.preview_image_url,
        #             width=media_item.width,
        #             height=media_item.height,
        #             blurhash=media_item.blurhash,
        #             entry_id=db_entry.id,  # 关键：使用刚生成的 entry.id
        #         )
        #         session.add(db_media)

    except Exception as e:
        session.rollback()
        log_error(f"数据库保存失败: {e}   {payload}")

    # try:
    #     await send_to_feishu(payload)
    # except httpx.RequestError as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail=f"网络错误: {e}",
    # #     )
    return {"ok": True}
