from typing import List, Optional, Tuple
import reflex as rx
from sqlmodel import Session, func, select
from aladdin.models.tag import Tag
from aladdin.templates import template
from aladdin.db import engine
from collections import defaultdict
from aladdin.utils.logger import log_debug


class TagState(rx.State):
    tags: List[Optional[Tag]] = []
    tag_group_count: List[Tuple[str, int, str]] = []
    tags_timeline: List[Tuple[str, List[Tag]]] = []  # ✅ 类型注解
    limit: int = 20
    offset: int = 0

    def tags_timeline_1(self) -> list:
        # 按日期分组
        tags_by_date = defaultdict(list)
        for tag in self.tags:
            date_str = (
                tag.updated_at.strftime("%Y-%m-%d") if tag.updated_at else "未知日期"
            )
            tags_by_date[date_str].append(tag)

        # 排序日期（最新在前）
        result = [
            (date, tags_by_date[date])
            for date in sorted(tags_by_date.keys(), reverse=True)
        ]
        self.tags_timeline = result

    def load_tag_data(self) -> None:
        self.search_tag()
        self.count_tag()

    @rx.event
    def search_tag(self, tag: str = None) -> None:
        if tag:
            with Session(engine) as session:
                statement = (
                    select(Tag)
                    .where(Tag.tag == tag)
                    .order_by(Tag.updated_at.desc())
                    .limit(self.limit)
                    .offset(self.offset)
                )
                self.tags = session.exec(statement).all()
        else:
            with Session(engine) as session:
                statement = (
                    select(Tag)
                    .order_by(Tag.updated_at.desc())
                    .limit(self.limit)
                    .offset(self.offset)
                )
                self.tags = session.exec(statement).all()
        self.tags_timeline_1()

    # 写一个统计tag个数的查询方法，需要按照时间、feedid筛选
    @rx.event
    def count_tag(self, tag: int = None, feed_id: str = None) -> None:
        with Session(engine) as session:
            # 统计 tag 出现的次数
            statement = (
                select(Tag.tag, func.count(Tag.id).label("count"), Tag.type)
                .group_by(Tag.tag, Tag.type)  # ✅ 把 type 加进去
                .order_by(func.count(Tag.id).desc())
                .limit(30)
            )

            self.tag_group_count = session.exec(statement).all()
            log_debug(self.tag_group_count)


@template(
    route="/tags",
    title="研报查询",
    on_load=[
        TagState.load_tag_data,
    ],
)
def tags_page() -> rx.Component:
    return rx.fragment(
        rx.heading("标签列表"),
        rx.vstack(
            # 展示标签统计，支持点击之后，筛选tag
            rx.box(
                rx.flex(
                    rx.foreach(
                        TagState.tag_group_count,
                        lambda tag: rx.badge(
                            f"{tag[0]}:{tag[1]}",
                            on_click=TagState.search_tag(tag=tag[0]),
                        ),
                    ),
                    flex_wrap="wrap",
                    gap="8px",
                ),
                rx.text("标签统计"),
            ),
            rx.grid(
                rx.foreach(
                    TagState.tags_timeline,
                    lambda dateinfo: rx.vstack(
                        rx.heading(dateinfo[0], size="5"),
                        rx.grid(
                            rx.foreach(
                                dateinfo[1],
                                lambda tag: rx.card(
                                    rx.vstack(
                                        rx.heading(tag.title, size="5"),  # 标签名
                                        rx.text(
                                            tag.description, size="4", color="gray"
                                        ),  # 内容标题
                                        rx.badge(tag.type, color_scheme="blue"),  # 类型
                                        rx.hstack(
                                            rx.badge(
                                                (f"{tag.direction}:{tag.tag}"),
                                                color_scheme=(
                                                    rx.cond(
                                                        tag.direction == "利好",
                                                        "green",
                                                        "red",
                                                    )
                                                ),
                                            ),
                                            rx.badge(
                                                f"置信度: {tag.confidence:.2f}",
                                                color_scheme="purple",
                                            ),
                                        ),
                                        align="start",
                                        spacing="2",
                                    ),
                                    variant="surface",
                                    # size="5",
                                    # shadow="md",
                                    border_radius="lg",
                                    # padding="1",
                                    # width="250px",
                                    _hover={"shadow": "xl", "transform": "scale(1.02)"},
                                ),
                            ),
                            columns="4",  # 每行显示4列
                            spacing="4",
                            justify="start",
                        ),
                    ),
                ),
            ),
        ),
    )
