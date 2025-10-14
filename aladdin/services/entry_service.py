from sqlmodel import Session, func, select
from typing import List, Optional
from aladdin.models.entry import Entry
# 添加新的导入
from pymysql.err import OperationalError
import time
import random


class EntryService:
    def __init__(self, session: Session):
        self.session = session

    def get_entry_by_id(self, entry_id: str) -> Optional[Entry]:
        """根据ID查询entry"""
        return self.session.get(Entry, entry_id)

    def get_entries_by_feed_id(
        self, feed_id: str, offset: int = 0, limit: int = 100
    ) -> List[Entry]:
        """根据feedId查询entries（支持分页）"""
        statement = (
            select(Entry)
            .where(Entry.feedId == feed_id)
            .order_by(Entry.publishedAt.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement))

    def get_entries_count_by_feed_id(self, feed_id: str) -> List[Entry]:
        """根据feedId查询entries（支持分页）"""
        statement = select(func.count(Entry.id)).where(Entry.feedId == feed_id)
        return self.session.exec(statement).one()

    def create_entry(self, entry: Entry) -> Entry:
        """创建新的entry"""
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def update_entry(self, entry: Entry) -> Entry:
        """更新entry"""
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    # 修改为异步方法
    async def upsert(self, instance: Entry, keys: tuple) -> Entry:
        """
        用实例做 upsert：
        1. 根据 keys 指定的字段组合查重；
        2. 查到 → 更新非 None 字段；
        3. 没查到 → 插入该实例；
        返回已 flush/refresh 的实例。
        """
        Model = type(instance)

        # 构造 where 条件
        where = [getattr(Model, k) == getattr(instance, k) for k in keys]
        stmt = select(Model).where(*where)
        db_obj = self.session.exec(stmt).first()

        if db_obj:
            # 更新已有记录
            for col, val in instance.dict(exclude_unset=True).items():
                if val is not None:
                    setattr(db_obj, col, val)
            # 添加重试机制处理锁超时问题
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.session.flush()
                    self.session.refresh(db_obj)
                    break  # 成功执行则跳出循环
                except OperationalError as e:
                    if "Lock wait timeout exceeded" in str(e) and attempt < max_retries - 1:
                        # 等待随机时间后重试
                        wait_time = 0.1 * (2 ** attempt) + random.uniform(0, 0.1)
                        time.sleep(wait_time)
                        self.session.rollback()
                        continue
                    else:
                        raise  # 如果不是锁超时或已达最大重试次数，则重新抛出异常
            instance = db_obj
        else:
            instance = self.create_entry(instance)

        return instance