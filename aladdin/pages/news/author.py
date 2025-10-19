from pydantic import BaseModel
import reflex as rx
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from aladdin.pages.news.feeds import feedentry
from aladdin.templates import template
from aladdin.models.feed import Feed
from aladdin.models.entry import Entry
from aladdin.db import engine
from aladdin.services.supabase import get_supabase_client
from aladdin.utils.logger import log_debug
import reflex_chakra as rc


class table_class(BaseModel):
    columns: List[str]
    rows: List[List]


# 定义数据模型
class AuthorState(rx.State):
    # 作者信息
    author_name: str = ""
    author_platform: str = ""
    feed_count: int = 0

    # 条目信息
    entries: List[feedentry] = []
    total_entries: int = 0

    # 分析信息
    analysis_data: List[dict] = []

    # Feed信息
    feeds: List[Feed] = []
    data_table: table_class
    # 页面 Tab 切换：raw（原文）| tags（抽取标签）
    active_tab: str = "raw"

    @rx.event
    def set_active_tab(self, tab: str) -> None:
        self.active_tab = tab

    @rx.event
    async def load_author_data(self) -> None:
        """加载作者数据，包括关联的feeds和entries"""
        # 获取Supabase客户端
        supabase = await get_supabase_client()

        # 查询作者相关的feeds
        feed_response = (
            await supabase.table("feed")
            .select("*", count="exact")
            .eq("author_id", self.author_id)
            .execute()
        )
        self.feeds = [Feed(**feed) for feed in feed_response.data]
        self.feed_count = feed_response.count

        # 如果有feeds，获取相关的entries
        feed_ids: list = []
        if self.feeds:
            feed_ids = [feed.id for feed in self.feeds]
            entry_response = await (
                supabase.table("entry")
                .select("*,feed(platform,image)", count="plain")
                .in_("feedId", feed_ids)
                .order("publishedAt", desc=True)
                .execute()
            )
            self.entries = entry_response.data
            self.total_entries = entry_response.count

            # 获取作者信息（从第一个feed中获取）
            if self.feeds:
                self.author_name = self.feeds[0].title or "Unknown Author"
                self.author_platform = self.feeds[0].platform or "Unknown Platform"

        # 加载分析数据
        if feed_ids:
            await self.load_analysis_data(feed_ids)
        else:
            self.analysis_data = []
            self.data_table = table_class(columns=[], rows=[])

    @rx.event
    async def load_analysis_data(self, feed_ids: list) -> None:
        """加载分析数据"""
        supabase = await get_supabase_client()

        # 查询analysis表数据
        response = (
            await supabase.table("analysis")
            .select("*,entry(feedId)")
            .in_("entry.feedId", feed_ids)
            .execute()
        )
        self.analysis_data = response.data

        # 3. 生成前端要的格式
        columns = ["type", "name", "code", "target_price", "rating", "opinion"]
        rows = [[d[c] for c in columns] for d in self.analysis_data]

        self.data_table = table_class(
            columns=[c.capitalize() for c in columns],
            rows=rows,
        )
        log_debug(self.data_table)


def author_card() -> rx.Component:
    """作者卡片组件"""
    return rx.card(
        rx.vstack(
            # 作者头像和基本信息
            rx.hstack(
                rx.avatar(
                    src="https://example.com/avatar.jpg",
                    size="4",
                ),
                rx.vstack(
                    rx.heading(AuthorState.author_name, size="4"),
                    rx.flex(
                        rx.foreach(
                            AuthorState.feeds,
                            lambda feed: rc.badge(
                                f"{feed.platform}: {feed.title}",
                                variant="solid",
                                size="1",
                            ),
                        ),
                        spacing="2",
                        flex_wrap="wrap",
                        width="100%",
                    ),
                    spacing="1",
                ),
                spacing="4",
                align="center",
            ),
            # 作者统计信息
            rc.stat_group(
                rc.stat(
                    rc.stat_label("Total Entries"),
                    rc.stat_number(AuthorState.total_entries),
                ),
                # rc.stat(rc.stat_label("Last Updated"), rc.stat_number("2023-10-01")),
                spacing="6",
                margin_top="4",
            ),
            spacing="3",
        ),
        width="100%",
    )


def analysis_table() -> rx.Component:
    """分析信息表格组件"""
    return rx.card(
        rx.vstack(
            rx.heading("Analysis Information", size="4"),
            rx.cond(
                AuthorState.data_table.rows.length() > 0,
                rc.table_container(
                    rc.table(
                        headers=AuthorState.data_table.columns,
                        rows=AuthorState.data_table.rows,
                    )
                ),
                rx.text("暂无分析数据", color="gray"),
            ),
            spacing="3",
        ),
        width="100%",
    )


def entry_details() -> rx.Component:
    """条目详情组件"""
    return (
        rx.card(
            rx.vstack(
                rx.heading("Entry Details", size="4"),
                rc.table_container(
                    rc.table(
                        headers=AuthorState.data_table.columns,
                        rows=AuthorState.data_table.rows,
                    )
                ),
            ),
            spacing="3",
        ),
    )


def raw_entries() -> rx.Component:
    """原文信息组件（精简列表）"""
    return rx.card(
        rx.vstack(
            rx.heading("Entries", size="4"),
            rx.foreach(
                AuthorState.entries,
                lambda e: rx.hstack(
                    # rx.avatar(
                    #     src=e.get("feed").get("image") | "",
                    #     size="2",
                    # ),
                    rx.vstack(
                        rx.heading(e.title, size="3"),
                        rx.text(
                            e.get("description") | "",
                            size="2",
                            color="gray",
                            max_width="60ch",
                            overflow="hidden",
                            text_overflow="ellipsis",
                            display="-webkit-box",
                            webkit_line_clamp="2",
                            webkit_box_orient="vertical",
                        ),
                        rx.hstack(
                            rc.badge(
                                e.feed.platform,
                                variant="solid",
                                size="1",
                            ),
                            rx.text(
                                (e.get("publishedAt") | ""),
                                size="1",
                                color="gray",
                            ),
                            spacing="2",
                        ),
                        spacing="1",
                    ),
                    rx.link("原文", href=e.url, is_external=True),
                    justify="between",
                    width="100%",
                    align="start",
                    padding_y="6px",
                    border_bottom="1px solid",
                    border_color="gray.100",
                ),
            ),
            spacing="3",
        ),
        width="100%",
    )


@template(
    route="/author/[author_id]",
    title="Author",
    on_load=AuthorState.load_author_data,
)
def author_page() -> rx.Component:
    return rx.flex(
        rx.heading("Author Aggregation", size="6"),
        rx.text("Aggregated view of multiple feeds by author", color="gray"),
        # 作者卡片
        author_card(),
        # Tab 切换
        rx.hstack(
            rc.button(
                "原文",
                variant=rx.cond(AuthorState.active_tab == "raw", "solid", "surface"),
                color_scheme=rx.cond(AuthorState.active_tab == "raw", "blue", "gray"),
                on_click=AuthorState.set_active_tab("raw"),
            ),
            rc.button(
                "抽取标签",
                variant=rx.cond(AuthorState.active_tab == "tags", "solid", "surface"),
                color_scheme=rx.cond(AuthorState.active_tab == "tags", "blue", "gray"),
                on_click=AuthorState.set_active_tab("tags"),
            ),
            spacing="2",
        ),
        # 主体内容：原文 或 抽取标签表格
        rx.cond(
            AuthorState.active_tab == "raw",
            raw_entries(),
            entry_details(),
        ),
        # 分析信息表格
        # analysis_table(),
        # 条目详情（由 Tab 控制显示，默认不单独渲染）
        direction="column",
        spacing="6",
        padding="20px",
        width="100%",
    )
