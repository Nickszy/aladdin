import os
from typing import Dict, List

from aladdin.components.antdicon import antdicon
from ..templates import template
import reflex as rx
from datetime import datetime
import uuid

# from aladdin.components.antd_icons import antdicon
from aladdin.components.antdx import (
    antdconversation,
    antdwelcome,
    antdattachments,
    antdprompts,
    antdbubble,
    antdxsender,
)


def openai(
    client=None,
    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    key=os.getenv("OPENAI_API_KEY"),
    url=os.getenv("OPENAI_BASE_URL"),
):
    """Get the response from the API.

    Args:
        form_data: A dict with the current question.
    """
    from openai import OpenAI

    client = client or OpenAI(api_key=key, base_url=url)

    async def process(chat):
        # Start a new session to answer the question.
        session = client.chat.completions.create(
            model=model,
            messages=chat.get_messages(),
            stream=True,
        )

        # Stream the results, yielding after every word.
        for item in session:
            # 替换原代码中访问 choices[0] 的部分
            if item.choices and len(item.choices) > 0:
                delta = item.choices[0].delta.content
            else:
                delta = None  # 或处理空响应的逻辑
            chat.append_to_response(delta)
            yield

    return process


class ChatState(rx.State):
    """聊天状态管理"""

    # # 会话数据
    conversations: List[Dict] = [
        {"key": "default-0", "label": "What is Ant Design X?", "group": "Today"},
        {"key": "default-1", "label": "How to install components?", "group": "Today"},
        {"key": "default-2", "label": "New AGI Interface", "group": "Yesterday"},
    ]
    current_conversation_key: str = "default-0"
    message_history: Dict[str, List[Dict]] = {}  # 会话消息历史
    input_value: str
    is_loading: bool = False
    attachments_open: bool = False
    attached_files: List[Dict] = []
    process = openai

    async def process_message(self):
        async for value in self.process():
            yield value

        self.processing = False

        # Scroll to the last message.
        yield self.scroll_to_bottom()

    # # 热门话题和提示词数据
    hot_topics = [
        {
            "key": "1",
            "label": "Hot Topics",
            "children": [
                {
                    "key": "1-1",
                    "description": "What has Ant Design X upgraded?",
                    "icon": "<span style='color:#f93a4a'>1</span>",
                },
                {
                    "key": "1-2",
                    "description": "New AGI Hybrid Interface",
                    "icon": "<span style='color:#ff6565'>2</span>",
                },
                {
                    "key": "1-3",
                    "description": "2323",
                    "icon": "<span style='color:#ff8f1f'>3</span>",
                },
                {
                    "key": "1-4",
                    "description": "3232?",
                    "icon": "<span style='color:#ff8f1f'>3</span>",
                },
                {
                    "key": "1-5",
                    "description": "3232333sign X?",
                    "icon": "<span style='color:#ff8f1f'>3</span>",
                },
                {
                    "key": "1-6",
                    "description": "What 3333 are in Ant Design X?",
                    "icon": "<span style='color:#ff8f1f'>3</span>",
                },
            ],
        }
    ]

    design_guide = [
        {
            "key": "2",
            "label": "Design Guide",
            "children": [
                {
                    "key": "2-1",
                    "icon": "calendar",
                    "label": "Intention",
                    "description": "AI understands user needs",
                },
                {
                    "key": "2-2",
                    "icon": "calendar",
                    "label": "Role",
                    "description": "AI's public persona",
                },
            ],
        }
    ]

    sender_prompts = [
        {"key": "1", "description": "Upgrades", "icon": "calendar"},
        {"key": "2", "description": "Components", "icon": "calendar"},
    ]

    @rx.var
    def current_messages(self) -> List[Dict]:
        """获取当前会话的消息"""
        return self.message_history.get(self.current_conversation_key, [])

    @rx.var
    def current_message_is_not_null(self) -> bool:
        return len(self.current_messages) != 0

    def create_new_conversation(self):
        """创建新会话"""
        new_key = str(uuid.uuid4())
        self.conversations.insert(
            0,
            {
                "key": new_key,
                "label": f"New Conversation {len(self.conversations) + 1}",
                "group": "Today",
            },
        )
        self.current_conversation_key = new_key
        self.message_history[new_key] = []

    def switch_conversation(self, value: str):
        """切换会话"""
        self.current_conversation_key = value
        if value not in self.message_history:
            self.message_history[value] = []
        yield self.scroll_to_bottom()

    def delete_conversation(self, key: str):
        """删除会话"""
        self.conversations = [c for c in self.conversations if c["key"] != key]
        if self.current_conversation_key == key:
            self.current_conversation_key = (
                self.conversations[0]["key"] if self.conversations else ""
            )
        del self.message_history[key]

        # 模拟AI回复
        self.is_loading = True
        yield  # 等待UI更新
        ai_msg = {
            "role": "assistant",
            "content": f"Response to: {content} (Simulated reply)",
        }
        self.message_history[self.current_conversation_key] = [
            *self.current_messages(),
            user_msg,
            ai_msg,
        ]
        self.is_loading = False
        self.input_value = ""

    def handle_input_change(self, value: str):
        """输入框变化"""
        self.input_value = value

    def toggle_attachments(self):
        """切换附件面板"""
        self.attachments_open = not self.attachments_open

    def send_message(self, info):
        """切换附件面板"""
        user_msg = {
            "key": str(uuid.uuid4()),
            "role": "user",
            "content": f'Response to: {info["data"]["description"]} (Simulated reply)',
        }
        self.message_history[self.current_conversation_key] = [
            *self.current_messages,
            user_msg,
            # ai_msg,
        ]
        yield self.scroll_to_bottom()

    @rx.event
    def send(self, msg):
        user_msg = {
            "key": str(uuid.uuid4()),
            "role": "user",
            "content": msg,
        }
        self.message_history[self.current_conversation_key] = [
            *self.current_messages,
            user_msg,
            # ai_msg,
        ]
        self.input_value = ""
        if self.current_message_is_not_null:
            yield self.scroll_to_bottom()
        self.message_history[self.current_conversation_key].append(
            {"role": "assistant", "content": ""}
        )
        self.is_loading = True
        yield type(self).process_message

    def scroll_to_bottom(self):
        return rx.call_script(
            f"""
            var element = document.getElementById('{self.current_conversation_key}');
            element.scrollTop = element.scrollHeight;
            """
        )


def chat_sider() -> rx.Component:
    """左侧会话面板"""
    return rx.box(
        # Logo
        rx.hstack(
            rx.image(
                src="https://mdn.alipayobjects.com/huamei_iwk9zp/afts/img/A*eco6RrQhxbMAAAAAAAAAAAAADgCCAQ/original",
                width="24px",
                height="24px",
            ),
            rx.text("Ant Design X", font_weight="bold", font_size="16px"),
            padding="0 24px",
            margin="24px 0",
            gap="8px",
        ),
        # 新建会话按钮
        rx.button(
            "New Conversation",
            on_click=ChatState.create_new_conversation,
            style={
                # "background": "#1677ff0f",
                "border": "1px solid #1677ff34",
                "height": "40px",
                "width": "100%",
            },
        ),
        # # 会话列表（antdx组件）
        antdconversation(
            items=ChatState.conversations,
            # default_active_key=ChatState.current_conversation_key,
            menu={"items": [{"label": "Delete"}]},
            active_key=ChatState.current_conversation_key,
            on_active_change=ChatState.switch_conversation,
            class_name="conversations",
            style={"item": {"padding": "0 8px"}},
            flex=1,
        ),
        # 底部区域
        rx.hstack(
            rx.avatar(src="/favicon.ico"),
            rx.icon("badge-info"),
            # rx.button(
            #     style={
            #         "background": "transparent",
            #         "border": "none",
            #         "padding": "0",
            #     },
            # ),
            justify_content="space-between",
            border_top="1px solid #e8e8e8",
            height="40px",
            padding="0 12px",
            display="flex",
            align_items="center",
        ),
        height="100%",
        width="280px",
        display="flex",
        flex_direction="column",
        box_sizing="border-box",
    )


def chat_area() -> rx.Component:
    """右侧聊天区域"""
    return rx.vstack(
        # 消息列表（antdx Bubble组件）
        # rx.box(
        rx.heading(ChatState.current_conversation_key),
        rx.cond(
            ChatState.current_message_is_not_null,
            rx.box(
                # rx.text(ChatState.current_conversation_key),
                # rx.text(ChatState.message_history),
                # 消息列表
                rx.foreach(
                    ChatState.current_messages,
                    lambda message: antdbubble(
                        content=message.content,
                        placement=rx.cond(message.role == "user", "end", "start"),
                        padding="5px",
                        width="100%",
                    ),
                    # rx.text(message.role),
                ),
                id=ChatState.current_conversation_key,
                # overflow_y="auto",
                # flex_direction="column",
                #     align="start",
                # ),
                flex=1,
                overflow_y="auto",
                # flex_direction="column",
                # justify="start",
                # align="start",
                # align="start",
                # style={"flex": 1, "overflow-y": "auto"},
                width="100%",
            ),
            #     #     roles={
            #     #         "assistant": {
            #     #             "placement": "start",
            #     #             "footer": AntdFlex(
            #     #                 AntdButton(
            #     #                     icon=antdicon.ReloadOutlined(),
            #     #                     size="small",
            #     #                     type="text",
            #     #                 ),
            #     #                 AntdButton(
            #     #                     icon=antdicon.CopyOutlined(),
            #     #                     size="small",
            #     #                     type="text",
            #     #                 ),
            #     #                 AntdButton(
            #     #                     icon=antdicon.LikeOutlined(),
            #     #                     size="small",
            #     #                     type="text",
            #     #                 ),
            #     #                 AntdButton(
            #     #                     icon=antdicon.DislikeOutlined(),
            #     #                     size="small",
            #     #                     type="text",
            #     #                 ),
            #     #                 gap="4px",
            #     #             ),
            #     #             "loadingRender": lambda: AntdSpin(size="small"),
            #     #         },
            #     #         "user": {"placement": "end"},
            #     #     },
            #     # 空状态（antdx Welcome组件）
            rx.vstack(
                rx.box(
                    antdwelcome(
                        icon="https://mdn.alipayobjects.com/huamei_iwk9zp/afts/img/A*s5sNRo5LjfQAAAAAAAAAAAAADgCCAQ/fmt.webp",
                        title="Hello, I'm Ant Design X",
                        description="Base on Ant Design, AGI product interface solution",
                        # extra=rx.box(
                        #     AntdButton(icon=antdicon.ShareAltOutlined()),
                        #     AntdButton(icon=antdicon.EllipsisOutlined()),
                        # ),
                    ),
                    rx.flex(
                        antdprompts(
                            items=ChatState.hot_topics,
                            on_item_click=ChatState.send_message,
                            styles={
                                "item": {
                                    "flex": 1,
                                    "background": "linear-gradient(123deg, #e5f4ff 0%, #efe7ff 100%)",
                                    "borderRadius": "12px",
                                }
                            },
                        ),
                        antdprompts(
                            items=ChatState.design_guide,
                            # on_item_click=lambda info: ChatState.send_message(
                            #     info["data"]["description"]
                            # ),
                            styles={
                                "item": {
                                    "flex": 1,
                                    "background": "linear-gradient(123deg, #e5f4ff 0%, #efe7ff 100%)",
                                    "borderRadius": "12px",
                                }
                            },
                        ),
                        gap="16px",
                    ),
                    direction="vertical",
                    gap="16px",
                    style={"paddingTop": "32px"},
                    padding_inline="calc(50% - 350px)",
                ),
                style={"flex": 1, "overflow-y": "auto"},
            ),
        ),
        # # # 提示词区域（antdx Prompts组件）
        # antdprompts(
        #     items=ChatState.sender_prompts,
        #     # on_item_click=ChatState.send_message,
        #     style={
        #         "width": "100%",
        #         "max-width": "700px",
        #         "margin": "0 auto",
        #         "color": "rgba(0,0,0,0.88)",
        #     },
        #     class_name="sender-prompt",
        # ),
        # 输入发送区域（antdx Sender组件）
        antdxsender(
            value=ChatState.input_value,
            on_change=ChatState.handle_input_change,
            on_submit=lambda msg: ChatState.send(msg),
            # # on_cancel=lambda a: ...,  # 可添加取消逻辑
            # loading=ChatState.is_loading,
            # prefix=rx.button(
            #     # icon=antdicon.PaperClipOutlined(size=18),
            #     type="text",
            #     onClick=ChatState.toggle_attachments,
            # ),
            submit_type="shiftEnter",
            style={"width": "100%", "maxWidth": "700px", "margin": "0 auto"},
        ),
        # style={
        #     "width": "100%",
        #     "display": "flex",
        #     "flexDirection": "column",
        #     "padding": "24px",
        #     "boxSizing": "border-box",
        #     "gap": "16px",
        # },
        height="100%",
        width="100%",
        display="flex",
        flex_direction="column",
        box_sizing="border-box",
    )


@template(route="/chatx", title="Ant Design X Chat")
def chatx() -> rx.Component:
    """主页面"""
    return rx.hstack(
        chat_sider(),
        chat_area(),
        style={
            "width": "100%",
            "height": "calc(100vh - 5em)",
            "min-width": "1000px",
            "display": "flex",
        },
    )
