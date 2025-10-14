import reflex as rx
from typing import List, Dict, Optional, Any, Callable
import uuid
from datetime import datetime


# 封装Ant Design图标（延续之前的封装）
class AntdIconComponent(rx.Component):
    library = "@ant-design/icons"
    tag = ""
    size: rx.Var[int] = 16
    color: rx.Var[str]

    def _get_imports(self) -> rx.utils.imports.ImportVar:
        return {self.library: [rx.utils.imports.ImportVar(self.tag)]}


class AntdIconNamespace:
    def __init__(self):
        icons = [
            "AppstoreAddOutlined",
            "CloudUploadOutlined",
            "CommentOutlined",
            "CopyOutlined",
            "DeleteOutlined",
            "DislikeOutlined",
            "EditOutlined",
            "EllipsisOutlined",
            "FileSearchOutlined",
            "HeartOutlined",
            "LikeOutlined",
            "PaperClipOutlined",
            "PlusOutlined",
            "ProductOutlined",
            "QuestionCircleOutlined",
            "ReloadOutlined",
            "ScheduleOutlined",
            "ShareAltOutlined",
            "SmileOutlined",
        ]
        for icon_name in icons:
            setattr(self, icon_name, self._create_icon(icon_name))

    def _create_icon(self, icon_name: str):
        def icon(**props) -> AntdIconComponent:
            component = AntdIconComponent(**props)
            component.tag = icon_name
            return component

        return icon


antdicon = AntdIconNamespace()
