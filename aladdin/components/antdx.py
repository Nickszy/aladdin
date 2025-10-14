# import reflex as rx
import reflex as rx
from reflex.utils.imports import ImportVar
from typing import List, Dict, Callable, Any, Optional


# 基础antdx组件封装类
class AntdxComponent(rx.Component):
    """基础Ant Design X组件封装"""

    library = "@ant-design/x"  # antdx库路径


# # 会话列表组件 (Conversations)
class AntdxConversations(AntdxComponent):
    tag = "Conversations"

    # 会话数据
    items: rx.Var[List[Dict]]
    # 当前激活的会话key
    active_key: rx.Var[str]
    default_active_key: rx.Var[str]
    # 会话切换回调
    on_active_change: rx.EventHandler[rx.event.passthrough_event_spec(str)]
    # 是否支持分组
    groupable: rx.Var[bool] = True


# 消息气泡列表组件 (Bubble.List)
class AntdxBubble(AntdxComponent):
    tag = "Bubble"

    # 消息数据
    content: rx.Var[str]
    # 角色配置
    placement: rx.Var[str] = "right"


# 输入发送组件 (Sender)
class AntdxSender(AntdxComponent):
    tag = "Sender"

    # 输入框值
    value: rx.Var[str]
    # 提交回调
    on_submit: rx.EventHandler[rx.event.passthrough_event_spec(str)]
    # # 输入变化回调
    on_change: rx.EventHandler[rx.event.passthrough_event_spec(str)]
    # # 取消回调
    # on_cancel: rx.Var[Callable[[], Any]]
    # 是否加载中
    loading: rx.Var[bool]
    # 前缀图标
    prefix: rx.Var[rx.Component]
    # 占位文本
    placeholder: rx.Var[str] = "Ask or input / use skills"
    # 是否允许语音输入
    allow_speech: rx.Var[bool] = False

    submit_type: rx.Var[str] = "enter"


# 提示词组件 (Prompts)
class AntdxPrompts(AntdxComponent):
    tag = "Prompts"

    # 提示词数据
    items: rx.Var[List[Dict]]
    # 点击回调
    on_item_click: rx.EventHandler[rx.event.passthrough_event_spec(str)]
    # 样式
    styles: rx.Var[Dict]
    # 类名
    class_name: rx.Var[str]


# 附件上传组件 (Attachments)
class AntdxAttachments(AntdxComponent):
    tag = "Attachments"

    # 文件列表
    # items: rx.Var[List[Dict]]
    # 变化回调
    on_change: rx.Var[Callable[[Dict], Any]]
    # 上传前回调（阻止默认上传）
    before_upload: rx.Var[Callable[[Any], bool]] = lambda _: False


# 欢迎组件 (Welcome)
class AntdxWelcome(AntdxComponent):
    tag = "Welcome"

    # 图标
    icon: rx.Var[str]
    # 标题
    title: rx.Var[str]
    # 描述
    description: rx.Var[str]
    # 额外内容
    extra: rx.Var[rx.Component]
    # 变体
    variant: rx.Var[str] = "borderless"


antdconversation = AntdxConversations.create
antdwelcome = AntdxWelcome.create
antdattachments = AntdxAttachments.create
antdprompts = AntdxPrompts.create
antdbubble = AntdxBubble.create
antdxsender = AntdxSender.create
