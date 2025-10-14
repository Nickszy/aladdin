# -----------------  元数据表  -----------------
from datetime import datetime
from typing import Optional
from sqlmodel import JSON, Column, Field, SQLModel


class FeedDatasource(SQLModel, table=True):
    __tablename__ = "feed_datasource"
    id: int = Field(primary_key=True)
    name: str
    db_url: str
    sql_text: str
    sort_field: str
    page_size: int = 500
    cron: Optional[str] = "0 */10 * * *"
    enabled: int = 1
    last_value: Optional[str] = None
    last_poll_time: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    replace: Optional[dict] = Field(default=None, sa_column=Column(JSON))
