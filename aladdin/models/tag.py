from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import json


class Tag(SQLModel, table=True):
    """
    标签数据模型，使用SQLModel实现数据库映射
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    entry_id: Optional[str] = Field(default=None, index=True)
    chat_id: Optional[str] = Field(default=None, index=True)
    tag: str = Field(default="")
    type: str = Field(default="")  # 行业或公司
    title: str = Field(default="")
    description: str = Field(default="")
    direction: str = Field(default="")  # 利好或利空
    confidence: float = Field(default=0.0)  # 置信度(0-1之间的数值)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
    is_valid: bool = Field(default=True)

    def to_dict(self) -> dict:
        """
        将Tag对象转换为字典

        Returns:
            dict: Tag数据字典
        """
        return {
            "id": self.id,
            "entry_id": self.entry_id,
            "chat_id": self.chat_id,
            "tag": self.tag,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "direction": self.direction,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        """
        从字典创建Tag对象

        Args:
            data: 包含Tag数据的字典

        Returns:
            Tag: Tag对象
        """
        return cls(
            entry_id=data.get("entry_id"),
            chat_id=data.get("chat_id"),
            tag=data.get("tag", ""),
            type=data.get("type", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            direction=data.get("direction", ""),
            confidence=float(data.get("confidence", 0.0)),
        )

    def to_json(self) -> str:
        """
        将Tag对象转换为JSON字符串

        Returns:
            str: JSON格式的Tag数据
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Tag":
        """
        从JSON字符串创建Tag对象

        Args:
            json_str: JSON格式的Tag数据

        Returns:
            Tag: Tag对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
