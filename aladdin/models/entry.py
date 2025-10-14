from dataclasses import dataclass
import re
from pydantic import BaseModel, HttpUrl
import sqlalchemy
from sqlmodel import JSON, Column, SQLModel, Field
from typing import List, Optional
from datetime import datetime

from aladdin.models.feed import Feed
from aladdin.models.tag import Tag
from aladdin.services.data_service import DataService
from aladdin.db import engine
import reflex as rx
from lxml import html as lxml_html


class Entry(SQLModel, table=True):
    __tablename__ = "entry"

    id: str = Field(default=None, primary_key=True, max_length=255)
    guid: str = Field(default=None, unique=True)
    feedId: str = Field(max_length=255)
    title: Optional[str] = Field(default=None, max_length=512)
    description: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None, max_length=255)
    url: str = None
    media: Optional[str] = Field(default=None)
    attachments: Optional[str] = Field(default=None)
    extra: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    publishedAt: datetime
    insertedAt: datetime = Field(default_factory=datetime.utcnow)

    @property
    def tags(self) -> List[Tag]:
        """通过实例属性获取标签（延迟查询）"""
        service = DataService(engine)
        data = Tag().where(Tag.entry_id == self.id).all()

        return service.search(data)

    # 将content去除html标签
    @property
    def content_text(self) -> str:
        tree = lxml_html.fromstring(self.content)
        # 2. 提取所有文本（strip=True 去除首尾空格）
        clean_str = tree.xpath("string(.)").strip()
        # 3. 优化文本格式
        clean_str = re.sub(r"\s+", " ", clean_str)
        return clean_str


# class Feed_read(BaseModel):
#     platform: Optional[str]


# class Entry_read(Entry):
#     feed: Optional[Feed_read] = None
