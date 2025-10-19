import openai
from openai import OpenAI, AsyncOpenAI
import asyncio
from typing import Dict, Any, Optional, List
from ..utils.logger import log_info, log_error


class AIService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = "1",
    ):
        """
        初始化AI服务

        Args:
            api_key: OpenAI API密钥
            base_url: OpenAI API基础URL（可选，用于支持其他兼容API）
            model: 默认模型名称
        """
        self.api_key = api_key
        self.model = model
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        if base_url:
            self.client.base_url = base_url

    async def request_openai(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        异步请求OpenAI接口返回数据

        Args:
            content: 请求内容
            model: 模型名称，例如 'gpt-3.5-turbo'，如果未提供则使用初始化时设置的默认模型
            **kwargs: 其他可选参数，如temperature, max_tokens等

        Returns:
            OpenAI接口返回的数据
        """
        # 如果未提供model参数，则使用初始化时设置的默认model

        # 如果仍然没有model，则抛出异常

        try:
            log_info("Starting OpenAI request")
            # 使用 asyncio.get_event_loop() 在线程池中运行阻塞操作
            loop = asyncio.get_event_loop()
            # 修改为使用新的API调用方式
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="model",
                    messages=[{"role": "user", "content": content}],
                    stream=False,
                ),
            )
            log_info(f"OpenAI request successful: {response}")
            return response
        except Exception as e:
            log_error(f"OpenAI request failed: {str(e)}")
            return {"error": str(e)}

    async def request_completion(
        self, prompt: str, model: Optional[str] = "ss", **kwargs
    ) -> Dict[str, Any]:
        """
        异步请求OpenAI Completion接口（适用于旧版模型如text-davinci-003）

        Args:
            prompt: 提示文本
            model: 模型名称，如果未提供则使用初始化时设置的默认模型
            **kwargs: 其他可选参数

        Returns:
            OpenAI Completion接口返回的数据
        """
        # 如果未提供model参数，则使用初始化时设置的默认model
        if model is None:
            model = self.model

        # 如果仍然没有model，则抛出异常
        if model is None:
            return {"error": "Model must be provided either in init or in method call"}

        try:
            # 使用 asyncio.get_event_loop() 在线程池中运行阻塞操作
            loop = asyncio.get_event_loop()
            # 修改为使用新的API调用方式
            response = await loop.run_in_executor(
                None,
                lambda: self.client.completions.create(
                    model=model, prompt=prompt, **kwargs
                ),
            )
            return response
        except Exception as e:
            return {"error": str(e)}
