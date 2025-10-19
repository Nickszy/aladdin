import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import List, Optional
from bs4 import BeautifulSoup
import httpx
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
from aladdin.utils.logger import log_debug, log_info, log_error

from typing import Optional
from pydantic import BaseModel, field_serializer, ConfigDict
from dataclasses import dataclass


# supabase = get_supabase_client()
class feed(BaseModel):

    id: str
    title: Optional[str]
    description: Optional[str]
    author_id: Optional[str]
    image: Optional[str]
    url: Optional[str]
    ownerUserId: Optional[str]
    ttl: Optional[int]
    language: Optional[str]
    platform: Optional[str]
    siteUrl: Optional[str]
    errorAt: Optional[datetime]
    errorMessage: Optional[str]
    lastModifiedHeader: Optional[str]
    etagHeader: Optional[str]
    checkedAt: Optional[datetime]


class entry_feed(BaseModel):
    author_id: Optional[str]
    image: Optional[str]
    title: Optional[str]
    platform: Optional[str]


class feedentry(BaseModel):
    model_config = ConfigDict(
        # 允许原始 datetime 字符串自动解析
        from_attributes=True,
        # 序列化时统一用东八区
        json_encoders={
            datetime: lambda v: v.astimezone(
                datetime.timezone(datetime.timedelta(hours=8))
            ).strftime("%Y-%m-%d %H:%M:%S")
        },
    )

    url: str
    id: str
    guid: str
    feedId: str
    title: Optional[str]
    description: Optional[str]
    content: Optional[str]
    author: Optional[str]
    media: Optional[str]
    attachments: Optional[List]
    extra: Optional[dict]
    publishedAt: datetime
    insertedAt: datetime
    updateAt: datetime
    feed: Optional[entry_feed]

    # 专门给 publishedAt 的序列化钩子
    @field_serializer("publishedAt")
    def serialize_cst(self, v: datetime) -> str:
        from datetime import timezone, timedelta  # 放函数里也行

        return v.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")


class FeedState(rx.State):
    platform: list = ["全部", "微博", "Twitter", "公众号", "Seeking Alpha", "其他"]
    platform_filter: str = None
    current_feed_id: List[str] = []
    current_feed: List[feed] = []  # 添加当前feed属性
    feeds: List[feed] = []
    total_feeds: int = 0
    current_page: int = 1
    feed_page_size: int = 30
    entries: List[Optional[feedentry]] = []
    tags: List[Optional[Tag]] = []
    total_entries: int = 0
    entries_current_page: int = 1
    entries_page_size: int = 24
    # 添加弹窗相关状态
    show_modal: bool = False
    selected_entry: Optional[feedentry] = None
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
            await statement.limit(self.feed_page_size)
            .offset(self.feed_page_size * (self.current_page - 1))
            .execute()
        )
        log_info(f"获取feed成功 {datetime.now()}")

        self.total_feeds = res.count
        self.feeds = [feed(**f) for f in res.data]

        await self.load_entries()

    @rx.event
    async def set_platform_filter(self, platform: str) -> None:
        self.platform_filter = platform
        self.current_page = 1
        await self.load_feeds()
        # await self._current_feed(self.feeds[0]["id"])

    @rx.event
    async def set_feed_page(self, page: int) -> None:
        log_debug(f"切换到 {page} 页")
        self.current_page = page
        await self.load_feeds()

    @rx.event
    async def ai_get_investment_analysis(self, entryid: str, content: str) -> None:
        try:
            URL = "http://100.64.0.2/v1/workflows/run"
            TOKEN = "app-Wt6BtPXy73jNGeYscForVBIU"
            headers = {
                "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "*/*",
                "Host": "100.64.0.2",
                "Connection": "keep-alive",
            }
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()

            # 添加 workflow_id 参数
            payload = {
                "inputs": {"text": text},
                "response_mode": "blocking",
                "user": "2323",
            }

            log_info(f"发送请求到: {URL}")
            # log_debug(f"Payload: {payload}")

            async with httpx.AsyncClient(timeout=300) as client:
                r = await client.post(URL, json=payload, headers=headers)
                log_info(f"响应状态码: {r.status_code}")
                log_info(f"响应内容: {r.text}")

                r.raise_for_status()
                data = r.json()

            # 调试输出
            log_debug(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

            # 修正数据提取逻辑
            if "data" in data and "outputs" in data["data"]:
                ret = json.loads(data["data"]["outputs"]["result"])
                log_debug(f"解析到的输出: {ret}")

                # 确保 ret 是列表
                if isinstance(ret, list):
                    for i in ret:
                        await self.insert_investment_analysis(entryid, i)
                else:
                    log_error(f"输出不是列表格式: {type(ret)}")
            else:
                log_error("响应中未找到 data.outputs 字段")

        except httpx.HTTPStatusError as e:
            log_error(f"HTTP错误: {e}")
            log_error(f"响应内容: {e.response.text}")
        except json.JSONDecodeError as e:
            log_error(f"JSON解析错误: {e}")
        except Exception as e:
            log_error(f"其他错误: {e}")

    async def insert_investment_analysis(self, entryid: str, data: dict) -> None:
        """
        插入投资分析数据到 Supabase
        """
        try:
            # 构建插入数据
            insert_data = {
                "entryid": entryid,
                "type": data["type"],
                "name": data["name"],
                "code": data["code"],
                "target_price": data["target_price"],
                "rating": data["rating"],
                "opinion": data["opinion"],
                "update_time": datetime.now().isoformat(),
                "is_valid": True,
            }

            # 插入数据
            supabase = await get_supabase_client()
            response = await supabase.table("analysis").upsert(insert_data).execute()

            if response.data:
                log_info("数据插入成功！")
                return response.data[0]
            else:
                log_error("数据插入失败")
                return None

        except Exception as e:
            log_error(f"插入数据时出错: {e}")
            return None

    @rx.event
    async def load_entries(self) -> None:
        if self.feed_id == "feed_id":
            return rx.redirect("/feeds")
        self.entries_current_page = 1
        # self.current_feed_id = "55854542499971072"
        log_debug(f"加载 {self.current_page} 页数据, feed_id: {self.current_feed_id}")
        await self._fetch_entries()

    @rx.event
    async def add_current_feed(self, feed: Feed):
        if feed not in self.current_feed:
            self.current_feed.append(feed)
            # print(f"增加feed {feed}")
            await self._fetch_entries()
        log_debug(f"当前feed: {self.current_feed}")

    # 添加删除单个选中feed的功能
    @rx.event
    async def remove_current_feed(self, feed: Feed):
        self.current_feed = [f for f in self.current_feed if f.id != feed.id]
        await self._fetch_entries()

    # 添加清空所有选中feed的功能
    @rx.event
    async def clear_current_feed(self):
        self.current_feed = []
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
        statement = supabase.table("entry").select(
            "*,feed!inner(platform,image,title,author_id)", count="exact"
        )
        if self.platform_filter:
            if self.platform_filter == "其他":
                statement = statement.not_.in_("feed.platform", self.platform)
            elif self.platform_filter == "全部":
                None
            else:
                statement = statement.eq("feed.platform", self.platform_filter)
        if self.current_feed != []:
            statement = statement.in_("feedId", [a.id for a in self.current_feed])
        res = (
            await statement.order("publishedAt", desc=True)
            .limit(self.entries_page_size)
            .offset((self.entries_current_page - 1) * self.entries_page_size)
            .execute()
        )
        log_info(f"获取entry成功 {datetime.now()}")
        self.entries = [feedentry(**entry) for entry in res.data]
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

    # 添加弹窗相关事件处理函数
    @rx.event
    async def open_modal(self, entry: feedentry) -> None:
        self.selected_entry = entry
        self.show_modal = True
        self.modal_html = process_img_src_in_html(self.selected_entry.content)

    @rx.event
    async def close_modal(self) -> None:
        self.show_modal = False
        self.selected_entry = None


def entry_card(entry: feedentry) -> rx.Component:
    return rx.card(
        rx.vstack(
            # 标题部分
            rx.hstack(
                rc.avatar(
                    src=entry.feed.image,
                    size="xs",
                    style={
                        "_hover": {"cursor": "pointer"},
                        "transition": "all 0.2s ease-in-out",
                    },
                ),
                rx.vstack(
                    rx.text(
                        entry.feed.title | "No Title",
                        size="2",
                        weight="bold",
                        style={
                            "_hover": {"cursor": "pointer"},
                            "transition": "all 0.2s ease-in-out",
                        },
                    ),
                    rx.badge(
                        entry.feed.platform | "Unknown",
                        color_scheme=rx.cond(
                            entry.feed.platform == "微博",
                            "pink",
                            rx.cond(
                                entry.feed.platform == "Twitter",
                                "blue",
                                rx.cond(
                                    entry.feed.platform == "公众号",
                                    "green",
                                    rx.cond(
                                        entry.feed.platform == "Seeking Alpha",
                                        "orange",
                                        "gray",
                                    ),
                                ),
                            ),
                        ),
                        radius="full",
                        size="1",
                    ),
                    spacing="1",
                ),
                spacing="2",
                justify="center",
                padding="5px",
                border="1px solid #eee",
                style={
                    "_hover": {"background_color": "#f0f8ff"},
                    "cursor": "pointer",
                    "transition": "all 0.2s ease-in-out",
                    "border_radius": "4px",
                },
            ),
            rx.cond(
                (entry.feed.platform != "微博") & (entry.feed.platform != "Twitter"),
                rx.vstack(
                    rx.cond(
                        entry.author,
                        rx.cond(
                            entry.feed.author_id,
                            rx.link(
                                rx.text(
                                    entry.author,
                                    size="2",
                                    weight="medium",
                                    color="gray.600",
                                ),
                                href=f"/author/{entry.feed.author_id}",
                            ),
                            rx.text(
                                entry.author,
                                size="2",
                                weight="medium",
                                color="gray.600",
                            ),
                        ),
                    ),
                    rx.heading(
                        entry.title,
                        size="3",
                        weight="bold",
                        color="gray.800",
                        line_height="1.3",
                        margin_bottom="12px",
                    ),
                    spacing="1",
                ),
                rx.cond(
                    entry.feed.author_id,
                    rx.link(
                        rx.heading(
                            entry.author,
                            size="3",
                            weight="bold",
                            color="gray.800",
                            line_height="1.3",
                            margin_bottom="12px",
                        ),
                        href=f"/author/{entry.feed.author_id}",
                    ),
                    rx.heading(
                        entry.author,
                        size="3",
                        weight="bold",
                        color="gray.800",
                        line_height="1.3",
                        margin_bottom="12px",
                    ),
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
                        rx.tooltip(
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
                                size="1",
                            ),
                            content=tag.title,
                        ),
                    ),
                ),
                wrap="wrap",
                spacing="2",
                margin_bottom="16px",
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
def entry_modal(entry: feedentry) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.cond(
                # 隐藏微博和推特的标题
                (entry.feed.platform.to(str) != "微博")
                & (entry.feed.platform.to(str) != "Twitter"),
                rx.dialog.title(
                    entry.author + entry.title,
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
                                "分析数据", size="3", weight="bold", margin_top="16px"
                            ),
                            rx.button(
                                "更新数据",
                                size="1",
                                color_scheme="blue",
                                variant="outline",
                                on_click=lambda: FeedState.ai_get_investment_analysis(
                                    entry.id, entry.content
                                ),
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


def filter() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("选择"),
                rx.foreach(
                    FeedState.platform,
                    lambda feed: rc.button(
                        feed, on_click=FeedState.set_platform_filter(feed)
                    ),
                ),
            ),
            # 修改为横向平铺展示
            rx.flex(
                rx.foreach(
                    FeedState.feeds,
                    lambda feed: rx.hstack(
                        rc.avatar(
                            src=feed.image,
                            size="xs",
                            on_click=FeedState.add_current_feed(feed),
                            style={
                                "_hover": {"cursor": "pointer"},
                                "transition": "all 0.2s ease-in-out",
                            },
                        ),
                        rx.text(
                            feed.title | "No Title",
                            size="2",
                            on_click=FeedState.add_current_feed(feed),
                            style={
                                "_hover": {"cursor": "pointer"},
                                "transition": "all 0.2s ease-in-out",
                            },
                        ),
                        spacing="2",
                        justify="center",
                        padding="5px",
                        border="1px solid #eee",
                        on_click=FeedState.add_current_feed(feed),
                        style={
                            "_hover": {"background_color": "#f0f8ff"},
                            "cursor": "pointer",
                            "transition": "all 0.2s ease-in-out",
                            "border_radius": "4px",
                        },
                    ),
                ),
                spacing="2",
                width="100%",
                max_height="300px",
                overflow_y="auto",
                flex_wrap="wrap",
            ),
            rx.hstack(
                rc.button(
                    "Previous",
                    on_click=FeedState.set_feed_page(FeedState.current_page - 1),
                    is_disabled=FeedState.current_page == 1,
                ),
                rc.text(
                    f"Page {FeedState.current_page}/{FeedState.total_feeds // FeedState.feed_page_size + 1}"
                ),
                rc.button(
                    "Next",
                    on_click=FeedState.set_feed_page(FeedState.current_page + 1),
                    is_disabled=FeedState.current_page * FeedState.feed_page_size
                    >= FeedState.total_feeds,
                ),
                spacing="1",
                margin_top="20px",
                align="center",
            ),
            # 显示已选中的feeds
            rx.cond(
                FeedState.current_feed.length() > 0,
                rx.hstack(
                    rx.text("已选中:", size="3", weight="bold", margin_top="10px"),
                    rx.foreach(
                        FeedState.current_feed,
                        lambda feed: rx.hstack(
                            rx.text(feed.title | "No Title", size="2"),
                            rc.button(
                                "删除",
                                on_click=FeedState.remove_current_feed(feed),
                                size="sm",
                                height="20px",
                                color_scheme="red",
                            ),
                            spacing="2",
                            align="center",
                            padding="3px",
                        ),
                    ),
                    rc.button(
                        "清空选中",
                        on_click=FeedState.clear_current_feed(),
                        size="sm",
                        color_scheme="red",
                        margin_top="5px",
                    ),
                    spacing="1",
                    width="100%",
                    align="center",
                ),
            ),
            spacing="3",
        ),
    )


# @template(
#     route="/entries/[feed_id]", title="Feed Entries", on_load=FeedState.load_entries
# )
# def entries_page() -> rx.Component:
#     # 初始化加载数据
#     return rx.fragment(
#         # 添加弹窗组件
#         entry_modal(),
#         rx.flex(
#             # 修改: 添加顶部标题和返回按钮
#             rx.hstack(
#                 rx.heading("Feed Entries"),
#                 rx.spacer(),
#                 rc.button(
#                     "Back to Feeds",
#                     on_click=rx.redirect("/feeds"),
#                     variant="solid",
#                     color_scheme="blue",
#                 ),
#                 width="100%",
#                 align_items="center",
#                 margin_bottom="10px",
#             ),
#             feed_info_card(),  # 添加feed信息卡片
#             # 修改为网格布局，每行1列以适配移动端
#             rx.grid(
#                 rx.foreach(FeedState.entries, entry_card),
#                 width="100%",
#                 gap="4",
#                 grid_template_columns=[
#                     "1fr",
#                     "repeat(1, 1fr)",
#                     "repeat(2, 1fr)",
#                     "repeat(2, 1fr)",
#                     "repeat(3, 1fr)",
#                 ],
#             ),
#             rx.hstack(
#                 rc.button(
#                     "Previous",
#                     on_click=FeedState.set_page(FeedState.current_page - 1),
#                     is_active=FeedState.current_page > 0,
#                 ),
#                 rc.text(f"Page {FeedState.current_page}"),
#                 rc.button(
#                     "Next",
#                     on_click=FeedState.set_page(FeedState.current_page + 1),
#                     is_active=FeedState.current_page * FeedState.page_size
#                     <= FeedState.total_entries,
#                 ),
#                 spacing="1",
#                 margin_top="20px",
#             ),
#             # 修改: 添加总数显示
#             rx.text(
#                 f"Total entries: {FeedState.total_entries}",
#                 size="3",
#                 margin_top="10px",
#                 text_align="center",
#             ),
#             flex_direction="column",
#             padding="20px",
#             # on_mount=lambda: FeedState.load_entries(),
#         ),
#         # on_mount=FeedState.load_entries,
#     )


@template(
    route="/feeds",
    title="Feeds",
    on_load=[FeedState.load_feeds],
)
def feeds_page() -> rx.Component:
    return rx.flex(
        rx.heading("Feeds"),
        filter(),
        rx.fragment(
            # 添加弹窗组件
            entry_modal(FeedState.selected_entry),
            rx.flex(
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
                        is_active=FeedState.entries_current_page > 0,
                    ),
                    rc.text(f"Page {FeedState.entries_current_page}"),
                    rc.button(
                        "Next",
                        on_click=FeedState.set_page(FeedState.entries_current_page + 1),
                        is_active=FeedState.entries_current_page
                        * FeedState.entries_page_size
                        <= FeedState.total_entries,
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
