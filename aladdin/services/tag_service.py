from typing import Any, Dict, List

from sqlmodel import Session, select
from aladdin.db import get_session, engine
from aladdin.models.entry import Entry
from aladdin.services.ai_service import AIService
from aladdin.models.tag import Tag
import json
import logging
from aladdin.utils.logger import log_info, log_error, log_debug

# 设置日志
logger = logging.getLogger(__name__)


class TaggingService:

    def __init__(self, ai_service: AIService, session: Session):
        """
        初始化打标服务

        Args:
            ai_service: AI服务实例
        """
        self.ai_service = ai_service
        self.session = session

    async def generate_tags_for_entry(self, entry_content: str) -> List[Tag]:
        """
        为新条目生成标签

        Args:
            entry_content: 条目内容

        Returns:
            标签列表，每个标签包含tag, type, title, description, direction, confidence字段
        """

        response = await self.ai_service.request_openai(
            content=entry_content,
            # model="gpt-3.5-turbo",  # 可根据需要调整模型
            # temperature=0.7,
            # max_tokens=2000,
        )

        # 解析AI返回的结果
        if "error" in response:
            raise Exception(f"AI服务调用失败: {response['error']}")

        # 这里需要根据实际的返回格式进行解析
        # 假设返回的是完整的JSON格式
        try:
            log_info("AI返回结果:")
            log_info(response)
            # 提取AI返回的文本内容
            ai_text = response.choices[0].message.content

            # 解析JSON（实际实现中可能需要更复杂的解析逻辑）

            # 需要处理可能的格式问题，比如代码块包裹等
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0]
            elif "```" in ai_text:
                ai_text = ai_text.split("```")[1].split("```")[0]

            tags_data = json.loads(ai_text)

            # 转换为Tag对象列表
            tags = [Tag.from_dict(tag_data) for tag_data in tags_data]
            return tags, response.id
        except Exception as e:
            raise Exception(f"解析AI返回结果失败: {str(e)}, AI返回结果: {response}")

    def save_tags_to_database(self, tags: List[Tag], entry_id: str, chat_id: str):
        """
        将标签数据保存到数据库

        Args:
            tags: 标签数据列表
            entry_id: 条目ID
        """
        # 替换为真实的数据库插入操作
        for tag in tags:
            tag.entry_id = entry_id
            tag.chat_id = chat_id
            tag.is_valid = True
            self.session.add(tag)
        self.session.commit()
        logger.info(f"Saved {len(tags)} tags to database for entry {entry_id}")

    async def process_new_entry(self, entry: Entry):
        """
        处理新条目，生成标签并保存到数据库

        Args:
            entry_content: 条目内容
            entry_id: 条目ID
        """
        try:
            # 调用AI生成标签
            log_info(f"Generating tags for entry {entry.id}...")
            tags, chat_id = await self.generate_tags_for_entry(entry.content_text)

            # 把之前的标签置否
            statement = select(Tag).where(Tag.entry_id == entry.id)
            before_tags = self.session.execute(statement).scalars().all()
            for tag in before_tags:
                tag.is_valid = False
                self.session.add(tag)
            self.session.commit()

            # 保存标签到数据库
            self.save_tags_to_database(tags, entry.id, chat_id)

            return tags
        except Exception as e:
            # 记录错误日志
            log_error(f"处理条目 { entry.id} 时出错: {str(e)}")
            raise
