from typing import Generator
from sqlalchemy import Sequence, create_engine
from sqlmodel import SQLModel, Session, select


wewe_mysql_url = "mysql+pymysql://reflex:reflex123!@rm-bp1c40h360600gb7m8o.mysql.rds.aliyuncs.com:3306/wewe-rss?charset=utf8mb4"

wewe_engine = create_engine(wewe_mysql_url)


aliyun_mysql_url = "mysql+pymysql://reflex:reflex123!@rm-bp1c40h360600gb7m8o.mysql.rds.aliyuncs.com:3306/folo?charset=utf8mb4"

engine = create_engine(aliyun_mysql_url)


def get_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


def upsert(
    session: Session,
    instance: SQLModel,
    keys: Sequence[str],
) -> SQLModel:
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
