from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class sql_Feed(SQLModel, table=True):
    __tablename__ = "feed"

    id: str = Field(default=None, primary_key=True, max_length=100)
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    image: Optional[str] = Field(default=None, max_length=255)
    url: str = Field(max_length=255)
    ownerUserId: Optional[str] = Field(default=None, max_length=255)
    ttl: Optional[int] = Field(default=None)
    language: Optional[str] = Field(default=None, max_length=255)
    platform: Optional[str] = Field(default=None, max_length=255)
    siteUrl: str = Field(max_length=255)
    errorAt: Optional[datetime] = Field(default=None)
    errorMessage: Optional[str] = Field(default=None, max_length=255)
    lastModifiedHeader: Optional[str] = Field(default=None, max_length=255)
    etagHeader: Optional[str] = Field(default=None, max_length=255)
    checkedAt: datetime


from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Feed(BaseModel):
    id: str
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    image: Optional[str] = Field(default=None, max_length=255)
    url: str = Field(..., max_length=255)  # 必填
    ownerUserId: Optional[str] = Field(default=None, max_length=255)
    ttl: Optional[int] = None
    language: Optional[str] = Field(default=None, max_length=255)
    platform: Optional[str] = Field(default=None, max_length=255)
    siteUrl: str = Field(..., max_length=255)  # 必填
    errorAt: Optional[datetime] = None
    errorMessage: Optional[str] = Field(default=None, max_length=255)
    lastModifiedHeader: Optional[str] = Field(default=None, max_length=255)
    etagHeader: Optional[str] = Field(default=None, max_length=255)
    checkedAt: datetime  # 必填
