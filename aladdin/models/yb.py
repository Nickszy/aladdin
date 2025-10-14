from pydantic import computed_field
import reflex as rx
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import date


class IfindYb(SQLModel, table=True):
    __tablename__ = "ifindyb"

    seq: int = Field(primary_key=True)
    declaredate: Optional[date] = Field(default=None)
    f006v_yb003: Optional[str] = Field(default=None)  # 机构
    f007v_yb003: Optional[str] = Field(default=None)  # 作者
    f009n_yb003: Optional[str] = Field(default=None)
    f010v_yb003: Optional[str] = Field(default=None)
    f012v_yb003: Optional[str] = Field(default=None)
    rtime: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    hangye1: Optional[str] = Field(default=None)  # 行业分类
    hangye2: Optional[str] = Field(default=None)
    hangye3: Optional[str] = Field(default=None)
    hangye4: Optional[str] = Field(default=None)
    secname: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)
    ctime: Optional[str] = Field(default=None)
    isvalid: Optional[int] = Field(default=None)
