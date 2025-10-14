from sqlalchemy import BinaryExpression
from sqlmodel import SQLModel, Session, func, select
from typing import List, Optional, Union

# 添加新的导入
from pymysql.err import OperationalError
import time
import random
from sqlalchemy.orm import sessionmaker


class DataService:
    def __init__(self, engine):
        self.engine = engine

    def get_entry_by_id(self, instance: SQLModel, entry_id: str) -> Optional[SQLModel]:
        """根据ID查询entry"""
        Model = type(instance)
        # 修改为使用 with Session(engine) 写法
        with Session(self.engine) as session:
            try:
                result = session.get(Model, entry_id)
                return result
            except Exception as e:
                session.rollback()
                raise e

    def search(
        self,
        query_source: Union[type[SQLModel], BinaryExpression],
        offset: int = 0,
        limit: int = 100,
        order_by: str = None,
    ) -> List[SQLModel]:
        """
        通用查询方法，支持直接传递模型类（全表查询）或带where条件的查询

        参数:
            query_source: 可以是模型类（如Entry）或带where条件的表达式（如Entry.where(Entry.feedId == 123)
            offset: 分页偏移量，默认为0
            limit: 每页条数，默认为100
            order_by: 排序字段，默认为"publishedAt"
        """
        # 确定模型类和基础查询
        if isinstance(query_source, BinaryExpression):
            # 处理带where条件的查询
            model_cls = query_source.parent.entity_namespace
            statement = select(model_cls).where(query_source)
        else:
            # 处理直接传递模型类的全表查询
            model_cls = query_source
            statement = select(model_cls)

        # 处理排序
        order_field = getattr(model_cls, order_by, None)
        if order_field:
            statement = statement.order_by(order_field.desc())

        # 应用分页
        statement = statement.offset(offset).limit(limit)

        # 执行查询
        with Session(self.engine) as session:
            try:
                result = session.execute(statement).scalars().all()
                return result
            except Exception as e:
                session.rollback()
                raise e

    def count(self, instance: SQLModel, feed_id: str) -> List[SQLModel]:
        """根据feedId查询entries数量"""
        Model = type(instance)
        statement = select(func.count(Model))
        # 修改为使用 with Session(engine) 写法
        with Session(self.engine) as session:
            try:
                # 修改为使用session.execute()和scalar()
                result = session.execute(statement).scalar()
                return result
            except Exception as e:
                session.rollback()
                raise e

    def create(self, instance: SQLModel) -> SQLModel:
        """创建新的entry"""
        # 修改为使用 with Session(engine) 写法
        with Session(self.engine) as session:
            try:
                session.add(instance)
                session.commit()
                session.refresh(instance)
                return instance
            except Exception as e:
                session.rollback()
                raise e

    def update_entry(self, instance: SQLModel) -> SQLModel:
        """更新entry"""
        # 修改为使用 with Session(engine) 写法
        with Session(self.engine) as session:
            try:
                session.add(instance)
                session.commit()
                session.refresh(instance)
                return instance
            except Exception as e:
                session.rollback()
                raise e

    # 修改为异步方法
    async def upsert(self, instance: SQLModel, keys: tuple) -> SQLModel:
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
        with Session(self.engine) as session:
            db_obj = session.exec(stmt).first()

            if db_obj:
                # 更新已有记录
                for col, val in instance.dict(exclude_unset=True).items():
                    if val is not None:
                        setattr(db_obj, col, val)
                session.flush()
                session.refresh(db_obj)
                return db_obj

            # 新建
            session.add(instance)
            session.flush()
            session.refresh(instance)
            return instance
