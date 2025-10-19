from sqlmodel import Session, select
from typing import List, Optional
from aladdin.models.yb import IfindYb
from datetime import date
from ..utils.logger import log_debug


class YbService:
    def __init__(self, session: Session):
        self.session = session

    def get_yb_list(
        self,
        id: Optional[int] = None,
        org: Optional[str] = None,
        author: Optional[str] = None,
        industry: Optional[str] = None,
        code: Optional[str] = None,
        declare_date: Optional[date] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[IfindYb]:
        """获取研报列表，支持筛选和分页"""
        statement = select(IfindYb).where(IfindYb.isvalid == 1)
        if id:
            statement = statement.where(IfindYb.seq == id)
        if org:
            statement = statement.where(IfindYb.f006v_yb003 == org)
        if author:
            statement = statement.where(IfindYb.f007v_yb003.contains(author))
        if industry:
            statement = statement.where(IfindYb.hangye1 == industry)
        if code:
            statement = statement.where(IfindYb.code == code)
        if declare_date:
            statement = statement.where(IfindYb.declaredate == declare_date)
        log_debug(f"YB query statement: {statement.whereclause}")

        statement = statement.order_by(IfindYb.seq.desc()).offset(offset).limit(limit)

        # 转换为响应模型，带 full_title
        return list(self.session.exec(statement).all())

    def get_all_orgs(self) -> List[str]:
        """获取所有机构名称"""
        statement = select(IfindYb.f006v_yb003).where(IfindYb.isvalid == 1).distinct()
        result = self.session.exec(statement)
        return [org for org in result if org is not None]

    def get_all_authors(self) -> List[str]:
        """获取所有作者名称"""
        statement = select(IfindYb.f007v_yb003).where(IfindYb.isvalid == 1).distinct()
        result = self.session.exec(statement)
        return [author for author in result if author is not None]

    def get_all_industries(self) -> List[str]:
        """获取所有行业分类"""
        # statement = select(IfindYb.hangye1).where(IfindYb.isvalid == 1).distinct()
        # result = self.session.exec(statement)
        log_debug("Getting all industries")
        return [
            "宏观经济",
            "个股研究",
            "投资策略",
            "行业研究",
            "基金报告",
            "港股研究",
            "英文报告",
            "海外市场",
        ]
