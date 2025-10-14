"""Feed and Author Management Page."""

from pydantic import BaseModel, Field
import reflex as rx
import json
import httpx
from typing import List, Optional

from aladdin.services.supabase import get_supabase_client
from .profile import ProfileState
from ..templates import template


class FeedItem(BaseModel):
    """Feed item data model."""

    id: str
    title: Optional[str]
    description: Optional[str]
    image: Optional[str]
    url: Optional[str]
    siteUrl: Optional[str]
    author_id: Optional[str]
    selected: bool = Field(default=False, exclude=True)


class AuthorItem(BaseModel):
    """Author item data model."""

    id: str
    name: str
    avatar: Optional[str]
    describe: Optional[str]


class ManagementState(rx.State):
    """State for the management page."""

    # Feed related
    feeds: List[FeedItem] = []
    selected_feeds: List[str] = []

    # Author related
    authors: List[AuthorItem] = []
    selected_author: Optional[str] = None

    # Form fields for editing feed
    editing_feed_id: Optional[str] = None
    edit_title: str = ""
    edit_description: str = ""
    edit_image: str = ""
    edit_url: str = ""
    edit_site_url: str = ""

    # Loading states
    loading: bool = False
    saving: bool = False

    async def load_data(self):
        """Load feeds and authors data."""
        self.loading = True
        # 这里暂时使用模拟数据

        supabase = await get_supabase_client()
        supabase_feed = (
            await supabase.table("feed").select("*", count="planned").execute()
        )
        self.feeds = [FeedItem(**feed) for feed in supabase_feed.data]
        supabase_author = (
            await supabase.table("author").select("*", count="planned").execute()
        )

        self.authors = [AuthorItem(**author) for author in supabase_author.data]
        self.loading = False

    def toggle_feed_selection(self, feed_id: str):
        """Toggle feed selection."""
        if feed_id in self.selected_feeds:
            self.selected_feeds.remove(feed_id)
        else:
            self.selected_feeds.append(feed_id)

    def select_all_feeds(self):
        """Select all feeds."""
        self.selected_feeds = [feed.id for feed in self.feeds]

    def deselect_all_feeds(self):
        """Deselect all feeds."""
        self.selected_feeds = []

    def set_selected_author(self, author_id: str):
        """Set selected author."""
        self.selected_author = author_id

    def start_edit_feed(self, feed_id: str):
        """Start editing a feed."""
        feed = next((f for f in self.feeds if f.id == feed_id), None)
        if feed:
            self.editing_feed_id = feed_id
            self.edit_title = feed.title or ""
            self.edit_description = feed.description or ""
            self.edit_image = feed.image or ""
            self.edit_url = feed.url
            self.edit_site_url = feed.siteUrl

    def cancel_edit_feed(self):
        """Cancel editing a feed."""
        self.editing_feed_id = None
        self.edit_title = ""
        self.edit_description = ""
        self.edit_image = ""
        self.edit_url = ""
        self.edit_site_url = ""

    async def save_feed_edit(self):
        """Save feed edit."""
        if not self.editing_feed_id:
            return

        # Find and update the feed
        for i, feed in enumerate(self.feeds):
            if feed.id == self.editing_feed_id:
                self.feeds[i] = FeedItem(
                    id=feed.id,
                    title=self.edit_title,
                    description=self.edit_description,
                    image=self.edit_image,
                    url=self.edit_url,
                    siteUrl=self.edit_site_url,
                    author_id=feed.author_id,
                )
                supabase = await get_supabase_client()
                res = (
                    await supabase.table("feed")
                    .upsert(self.feeds[i].model_dump())
                    .execute()
                )
                print(self.feeds[i].model_dump(), res)

        self.cancel_edit_feed()

    def assign_feeds_to_author(self):
        """Assign selected feeds to the selected author."""
        if not self.selected_author or not self.selected_feeds:
            return

        # Update the author_id for selected feeds
        for i, feed in enumerate(self.feeds):
            if feed.id in self.selected_feeds:
                self.feeds[i] = FeedItem(
                    id=feed.id,
                    title=feed.title,
                    description=feed.description,
                    image=feed.image,
                    url=feed.url,
                    siteUrl=feed.siteUrl,
                    author_id=self.selected_author,
                )

        # Clear selection after assignment
        self.selected_feeds = []


def feed_card(feed: FeedItem) -> rx.Component:
    """Create a feed card component."""
    return rx.card(
        rx.flex(
            rx.checkbox(
                checked=rx.cond(
                    ManagementState.selected_feeds.contains(feed.id), True, False
                ),
                on_change=lambda checked: ManagementState.toggle_feed_selection(
                    feed.id
                ),
                size="3",
            ),
            rx.avatar(src=feed.image, size="3"),
            rx.vstack(
                rx.heading(feed.title, size="4"),
                rx.text(feed.description, size="2", color="gray"),
                rx.hstack(
                    rx.badge(feed.siteUrl, color_scheme="blue"),
                    rx.badge(feed.author_id, color_scheme="gray"),
                    spacing="2",
                ),
                spacing="2",
                width="100%",
            ),
            rx.dialog.root(
                rx.dialog.trigger(
                    rx.button(
                        "编辑",
                        on_click=lambda: ManagementState.start_edit_feed(feed.id),
                        variant="soft",
                        color_scheme="gray",
                    )
                ),
                rx.dialog.content(
                    feed_editor(),
                ),
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        width="100%",
    )


def author_selector() -> rx.Component:
    """Create an author selector component."""
    return rx.vstack(
        rx.heading("选择作者", size="4"),
        rx.scroll_area(
            rx.flex(
                rx.foreach(
                    ManagementState.authors,
                    lambda author: rx.button(
                        rx.hstack(
                            rx.avatar(
                                src=author.avatar, fallback=author.name[0], size="2"
                            ),
                            rx.text(author.name, size="2"),
                            spacing="2",
                        ),
                        on_click=lambda: ManagementState.set_selected_author(author.id),
                        variant=rx.cond(
                            ManagementState.selected_author != author.id,
                            "surface",
                            "solid",
                        ),
                        color_scheme=rx.cond(
                            ManagementState.selected_author == author.id, "blue", "gray"
                        ),
                        width="100%",
                    ),
                ),
                direction="column",
                spacing="2",
            ),
            type="auto",
            height="200px",
        ),
        spacing="3",
    )


def feed_editor() -> rx.Component:
    """Create a feed editor component."""
    return rx.card(
        rx.vstack(
            rx.heading("编辑 Feed", size="4"),
            rx.grid(
                rx.vstack(
                    rx.text("标题", size="2"),
                    rx.input(
                        value=ManagementState.edit_title,
                        on_change=ManagementState.set_edit_title,
                        placeholder="输入标题",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("描述", size="2"),
                    rx.text_area(
                        value=ManagementState.edit_description,
                        on_change=ManagementState.set_edit_description,
                        placeholder="输入描述",
                        min_height="100px",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("图片 URL", size="2"),
                    rx.input(
                        value=ManagementState.edit_image,
                        on_change=ManagementState.set_edit_image,
                        placeholder="输入图片 URL",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Feed URL", size="2"),
                    rx.input(
                        value=ManagementState.edit_url,
                        on_change=ManagementState.set_edit_url,
                        placeholder="输入 Feed URL",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("网站 URL", size="2"),
                    rx.input(
                        value=ManagementState.edit_site_url,
                        on_change=ManagementState.set_edit_site_url,
                        placeholder="输入网站 URL",
                    ),
                    spacing="1",
                ),
                gap="2",
                grid_template_columns="1fr 1fr",
            ),
            rx.flex(
                rx.button(
                    "取消",
                    on_click=ManagementState.cancel_edit_feed,
                    variant="soft",
                    color_scheme="gray",
                ),
                rx.button(
                    "保存", on_click=ManagementState.save_feed_edit, color_scheme="blue"
                ),
                justify="end",
                spacing="3",
            ),
            spacing="4",
        )
    )


@template(route="/management", title="管理", on_load=ManagementState.load_data)
def management() -> rx.Component:
    """The management page."""
    return rx.vstack(
        rx.heading(f"欢迎, {ProfileState.profile.name}", size="6"),
        rx.text("管理 Feed 和作者关联", size="4", color="gray"),
        rx.divider(),
        # Action buttons
        rx.flex(
            rx.button(
                "全选", on_click=ManagementState.select_all_feeds, variant="soft"
            ),
            rx.button(
                "取消全选", on_click=ManagementState.deselect_all_feeds, variant="soft"
            ),
            rx.spacer(),
            rx.button(
                f"分配给作者 ({ManagementState.selected_feeds.length()}))",
                on_click=ManagementState.assign_feeds_to_author,
                color_scheme="blue",
                disabled=rx.cond(
                    ManagementState.selected_feeds.length() == 0, True, False
                ),
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        # Main content area
        rx.grid(
            # Feed list
            rx.vstack(
                rx.heading("Feeds", size="5"),
                rx.divider(),
                rx.scroll_area(
                    rx.foreach(ManagementState.feeds, feed_card),
                    type="auto",
                    height="600px",
                ),
                spacing="4",
                width="100%",
            ),
            # Sidebar with author selector and editor
            rx.vstack(
                author_selector(),
                # rx.cond(ManagementState.editing_feed_id, feed_editor()),
                spacing="6",
                width="100%",
            ),
            gap="6",
            grid_template_columns=["1fr", "1fr", "2fr 1fr"],
        ),
        spacing="6",
        width="100%",
    )
