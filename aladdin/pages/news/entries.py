import asyncio
from datetime import datetime
from typing import List, Optional
import reflex as rx
import reflex_chakra as rc
from sqlmodel import Session

from aladdin.services.supabase import get_supabase_client  # as get_supabase_client
from aladdin.templates import template
from aladdin.models.feed import Feed
from aladdin.services.feed_service import FeedService
from aladdin.db import engine
from typing import List, Optional
import reflex as rx
import reflex_chakra as rc
from sqlmodel import Session, select

from aladdin.models.tag import Tag
from aladdin.services.data_service import DataService
from aladdin.templates import template
from aladdin.models.entry import Entry
from aladdin.models.feed import Feed  # 添加导入
from aladdin.services.entry_service import EntryService
from aladdin.services.feed_service import FeedService  # 添加导入
from aladdin.db import engine
from aladdin.utils.img_proxy import process_img_src_in_html
from aladdin.utils.logger import log_debug, log_info

# supabase = get_supabase_client()


class FeedState(rx.State):
    platform: list = ["全部", "微博", "Twitter", "公众号", "Seeking Alpha", "其他"]
    platform_filter: str = None
    feeds: List[dict] = []
    total_feeds: int = 0
    current_page: int = 1
    feed_page_size: int = 12
    entries: List[Optional[dict]] = []
    tags: List[Optional[Tag]] = []
    total_entries: int = 0
    entries_current_page: int = 1
    entries_page_size: int = 24
    current_feed_id: str = ""
    current_feed: Optional[dict] = None  # 添加当前feed属性
    # 添加弹窗相关状态
    show_modal: bool = False
    selected_entry: Optional[Entry] = None
    modal_html: str = ""

    @rx.event
    async def load_feeds(self) -> None:
        log_debug(self.platform_filter)
        log_info(f"获取feed {datetime.now()}")
        supabase = await get_supabase_client()
        statement = supabase.table("feed").select("*", count="planned")
        if self.platform_filter:

            if self.platform_filter == "其他":
                statement = statement.not_.in_("platform", self.platform)
            elif self.platform_filter == "全部":
                None
            else:
                statement = statement.eq("platform", self.platform_filter)

        res = (
            await statement.limit(12)
            .offset(self.feed_page_size * (self.current_page - 1))
            .execute()
        )
        log_info(f"获取feed成功 {datetime.now()}")

        self.total_feeds = res.count
        self.feeds = res.data

    @rx.event
    async def set_platform_filter(self, platform: str) -> None:
        self.platform_filter = platform
        self.current_page = 1
        await self.load_feeds()
        await self.set_current_feed(self.feeds[0]["id"])

    @rx.event
    async def set_feed_page(self, page: int) -> None:
        self.current_page = page
        await self.load_feeds()

    @rx.event
    async def load_entries(self) -> None:
        if self.feed_id == "feed_id":
            return rx.redirect("/feeds")
        self.current_page = 1
        self.current_feed_id = self.feed_id
        log_debug(f"加载 {self.current_page} 页数据, feed_id: {self.current_feed_id}")
        await self._fetch_feed_info()
        await self._fetch_entries()

    @rx.event
    async def set_page(self, page: int) -> None:
        self.entries_current_page = page
        log_debug(f"切换页面 {page}")
        await self._fetch_entries()

    # 获取相关的标签数据
    async def _fetch_tags(self) -> None:
        with Session(engine) as session:
            entry_ids = [i["id"] for i in self.entries]
            if entry_ids:
                statement = select(Tag).where(Tag.entry_id.in_(entry_ids))
                self.tags = session.execute(statement).scalars().all()
            else:
                self.tags = []

    async def _fetch_entries(self) -> None:
        log_debug(f"查询: {self.current_feed_id}")
        log_info(f"创建supabase {datetime.now()}")
        supabase = await get_supabase_client()
        log_info(f"创建supabase 成功 {datetime.now()}")
        log_info(f"获取entry {datetime.now()}")
        res = (
            await supabase.table("entry")
            .select("*", count="exact")
            .eq("feedId", self.current_feed_id)
            .order("publishedAt", desc=True)
            .limit(self.entries_page_size)
            .offset((self.entries_current_page - 1) * self.entries_page_size)
            .execute()
        )
        log_info(f"获取entry成功 {datetime.now()}")
        self.entries = res.data
        self.total_entries = res.count
        # with Session(engine) as session:
        #     service = EntryService(session)
        #     offset = (self.current_page - 1) * self.page_size
        #     self.entries = service.get_entries_by_feed_id(
        #         self.current_feed_id, offset=offset, limit=self.page_size
        #     )
        #     # # 获取总数需要额外查询，这里简化处理
        #     # self.total_entries = service.get_entries_count_by_feed_id(
        #     #     self.current_feed_id
        #     # )

    async def _fetch_feed_info(self) -> None:  # 添加获取feed信息的方法
        log_info(f"获取feed info {datetime.now()}")
        supabase = await get_supabase_client()
        res = (
            await supabase.table("feed")
            .select("*")
            .eq("id", self.current_feed_id)
            .execute()
        )
        log_info(f"获取feed info成功 {datetime.now()}")

        self.current_feed = res.data[0]

    # 添加弹窗相关事件处理函数
    @rx.event
    async def open_modal(self, entry: Entry) -> None:
        self.selected_entry = entry
        self.show_modal = True
        self.modal_html = process_img_src_in_html(self.selected_entry.content)

    @rx.event
    async def close_modal(self) -> None:
        self.show_modal = False
        self.selected_entry = None


def feed_info_card() -> rx.Component:  # 添加feed信息卡片组件
    return rx.cond(
        FeedState.current_feed,
        rc.card(
            rx.hstack(
                rx.cond(
                    FeedState.current_feed.image,
                    rc.avatar(
                        src=FeedState.current_feed.image,
                        border_radius="full",
                        size="md",
                    ),
                    rc.avatar(
                        name=FeedState.current_feed.title,
                        size="md",
                        color="gray.500",
                    ),
                ),
                rx.vstack(
                    rx.heading(FeedState.current_feed.title | "No Title", size="4"),
                    rx.text(FeedState.current_feed.description | "No description"),
                    rx.hstack(
                        rx.icon("calendar", size=16, color="gray.500"),
                        rx.text(
                            f"更新时间: {FeedState.current_feed.lastModifiedHeader}",
                            size="1",
                            color="gray.600",
                            font_weight="500",
                        ),
                        align_items="center",
                        gap="6px",
                    ),
                    rx.text(
                        f"数据来源：{FeedState.current_feed.platform}",
                        size="1",
                        color="blue.500",
                        font_weight="500",
                    ),
                ),
                # 最后发布时间
                spacing="3",
                align="center",
                max_width="1200px",
            ),
            width="100%",
            margin="10px",
        ),
    )


def entry_card(entry: Entry) -> rx.Component:
    return rx.card(
        rx.vstack(
            # 标题部分
            rx.cond(
                (FeedState.current_feed.platform != "微博")
                & (FeedState.current_feed.platform != "Twitter"),
                rx.heading(
                    entry.title,
                    size="3",
                    weight="bold",
                    color="gray.800",
                    line_height="1.3",
                    margin_bottom="12px",
                ),
            ),
            # 描述内容
            rx.text(
                entry.description,
                size="3",
                color="gray.700",
                line_height="1.6",
                margin_bottom="20px",
                # 限制描述长度，避免卡片过高
                overflow="hidden",
                text_overflow="ellipsis",
                display="-webkit-box",
                webkit_line_clamp="3",
                webkit_box_orient="vertical",
            ),
            rx.hstack(
                rx.foreach(
                    FeedState.tags,
                    lambda tag: rx.cond(
                        tag.entry_id == entry.id,
                        rx.badge(
                            tag.tag,
                            color_scheme=rx.cond(
                                tag.direction == "利好",
                                "green",
                                rx.cond(
                                    tag.direction == "利空",
                                    "red",
                                    "blue",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            # 发布时间
            rx.hstack(
                rx.icon("calendar", size=16, color="gray.500"),
                rx.text(
                    f"Published: {entry.publishedAt}",
                    size="1",
                    color="gray.600",
                    font_weight="500",
                ),
                align_items="center",
                gap="6px",
                margin_bottom="16px",
            ),
            spacing="0",
            align_items="start",
            width="100%",
        ),
        # 卡片样式
        width="100%",
        max_width="400px",
        padding="24px",
        margin="12px",
        border_radius="12px",
        border="1px solid",
        border_color="gray.200",
        background="white",
        box_shadow="sm",
        # 添加悬停动画效果
        cursor="pointer",
        transition="all 0.3s ease",
        _hover={
            "box_shadow": "lg",
            "border_color": "blue.300",
            "transform": "translateY(-4px)",
            "background": "linear-gradient(to bottom, #ffffff, #f9f9f9)",
        },
        # 修改: 点击整个卡片打开弹窗
        on_click=FeedState.open_modal(entry),
    )


# 添加弹窗组件
def entry_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.cond(
                # 隐藏微博和推特的标题
                (FeedState.current_feed.platform.to(str) != "微博")
                & (FeedState.current_feed.platform.to(str) != "Twitter"),
                rx.dialog.title(
                    FeedState.selected_entry.title,
                    size="4",
                    weight="bold",
                    padding_bottom="12px",
                    border_bottom="1px solid",
                    border_color="gray.200",
                ),
            ),
            rx.dialog.description(
                rx.scroll_area(
                    rx.vstack(
                        # 修改图片显示逻辑，支持更完整的图片数据结构
                        rx.html(FeedState.modal_html),
                        # rx.html(FeedState.selected_entry.content),
                        # 添加标签展示区域
                        rx.vstack(
                            rx.heading(
                                "Tags", size="3", weight="bold", margin_top="16px"
                            ),
                            rx.vstack(
                                rx.foreach(
                                    FeedState.tags,
                                    lambda tag: rx.cond(
                                        tag.entry_id == FeedState.selected_entry.id,
                                        rx.tooltip(
                                            rx.badge(
                                                f"{tag.tag}:{tag.title}",
                                                color_scheme=rx.cond(
                                                    tag.direction == "利好",
                                                    "green",
                                                    rx.cond(
                                                        tag.direction == "利空",
                                                        "red",
                                                        "blue",
                                                    ),
                                                ),
                                                variant="surface",
                                                size="2",
                                            ),
                                            # 修改: 将content改为字符串格式
                                            content=f"标签: {tag.tag}\n"
                                            + f"类型: {tag.type}\n"
                                            + f"描述: {tag.description}\n"
                                            + f"置信度: {tag.confidence}",
                                        ),
                                    ),
                                ),
                                spacing="2",
                                margin_top="8px",
                            ),
                            width="100%",
                        ),
                        # 展示图片
                        # rx.cond(
                        #     FeedState.selected_entry.media.length() > 0,
                        #     rx.text(FeedState.selected_entry.media),
                        # ),
                        # spacing="4",
                        # padding_y="16px",
                        # width="100%",
                        width="95%",
                    ),
                    type="always",
                    scrollbars="vertical",
                    height="70vh",
                ),
                padding_y="16px",
                max_height="700px",
            ),
            rx.flex(
                rx.dialog.close(
                    rc.button(
                        "Close",
                        color_scheme="gray",
                    ),
                ),
                rx.link(
                    rc.button(
                        "Read Original Article",
                        color_scheme="blue",
                    ),
                    href=FeedState.selected_entry.url,
                    is_external=True,
                    margin_left="12px",
                ),
                justify="end",
                spacing="3",
                margin_top="16px",
                padding_top="16px",
                border_top="1px solid",
                border_color="gray.200",
            ),
            max_width="70vw",
            width="100%",
        ),
        open=FeedState.show_modal,
        on_open_change=FeedState.close_modal,
    )


@template(route="/feed/[feed_id]", title="Feed Entries", on_load=FeedState.load_entries)
def feed_page() -> rx.Component:
    return rx.flex(
        rx.heading("Feeds"),
        rx.fragment(
            # 添加弹窗组件
            entry_modal(),
            rx.flex(
                feed_info_card(),  # 添加feed信息卡片
                # 修改为网格布局，每行1列以适配移动端
                rx.grid(
                    rx.foreach(FeedState.entries, entry_card),
                    width="100%",
                    gap="4",
                    grid_template_columns=[
                        "1fr",
                        "repeat(1, 1fr)",
                        "repeat(2, 1fr)",
                        "repeat(2, 1fr)",
                        "repeat(3, 1fr)",
                    ],
                ),
                rx.hstack(
                    rc.button(
                        "Previous",
                        on_click=FeedState.set_page(FeedState.entries_current_page - 1),
                        is_disabled=FeedState.entries_current_page == 1,
                    ),
                    rc.text(f"Page {FeedState.entries_current_page}"),
                    rc.button(
                        "Next",
                        on_click=FeedState.set_page(FeedState.entries_current_page + 1),
                        is_disabled=FeedState.entries_current_page
                        * FeedState.entries_page_size
                        >= FeedState.total_entries,
                    ),
                    spacing="1",
                    margin_top="20px",
                ),
                # 修改: 添加总数显示
                rx.text(
                    f"Total entries: {FeedState.total_entries}",
                    size="3",
                    margin_top="10px",
                    text_align="center",
                ),
                flex_direction="column",
                padding="20px",
                # on_mount=lambda: FeedState.load_entries(),
            ),
            # on_mount=FeedState.load_entries,
        ),
        flex_direction="column",
        padding="20px",
    )
