"""LLM parser for converting natural language to search queries."""

import json
from datetime import datetime, timedelta
from typing import Any

from loguru import logger
from openai import OpenAI

from src.config.settings import get_settings
from src.core.exceptions import (
    LLMConnectionError,
    LLMParseError,
    LLMResponseError,
    MissingAPIKeyError,
)
from src.core.models import SearchQuery

SYSTEM_PROMPT_TEMPLATE = """你是一个文件搜索查询解析器。用户会用自然语言描述他们想要搜索的文件，你需要将其转换为结构化的搜索参数。

今天的日期是：{today}

返回一个 JSON 对象，包含以下可选字段：
- pattern: 文件名模式（支持通配符 * 和 ?）
- extensions: 文件扩展名列表（例如 [".py", ".txt"]）
- min_size: 最小文件大小（字节数，整数）
- max_size: 最大文件大小（字节数，整数）
- modified_after: 修改时间晚于此日期（ISO 格式，如 "2024-01-01"）
- modified_before: 修改时间早于此日期（ISO 格式）
- content_pattern: 文件内容搜索模式
- include_hidden: 是否包含隐藏文件（默认 false）
- recursive: 是否递归搜索子目录（默认 true）

重要规则：
1. 只返回 JSON，不要有其他文字
2. 只包含用户明确提到的字段
3. 大小必须转换为字节数（整数）：1KB=1024, 1MB=1048576, 1GB=1073741824
4. 时间表达式必须转换为具体日期：
   - "最近一周" = 从 {week_ago} 到现在
   - "今天" = {today}
   - "昨天" = {yesterday}
5. 文件类型映射：
   - "Python 文件" -> [".py"]
   - "图片" -> [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
   - "视频" -> [".mp4", ".avi", ".mkv", ".mov", ".wmv"]
   - "文档" -> [".doc", ".docx", ".pdf", ".txt", ".md"]

示例：
输入: "找出最近一周修改的大于10MB的Python文件"
输出: {{"extensions": [".py"], "min_size": 10485760, "modified_after": "{week_ago}"}}
"""


def _parse_size(size_str: str) -> int:
    """Parse size string to bytes.

    Args:
        size_str: Size string like "10MB" or "1.5GB".

    Returns:
        Size in bytes.
    """
    size_str = size_str.strip().upper()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            num_str = size_str[: -len(unit)].strip()
            return int(float(num_str) * multiplier)

    return int(size_str)


class LLMParser:
    """Parser that uses LLM to convert natural language to SearchQuery.

    Attributes:
        client: OpenAI client instance.
        model: Model name to use.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize the LLM parser.

        Args:
            api_key: OpenAI API key. If None, uses settings.
            model: Model name. If None, uses settings.

        Raises:
            MissingAPIKeyError: If no API key is configured.
        """
        settings = get_settings()

        self.api_key = api_key or settings.llm.api_key
        if not self.api_key:
            raise MissingAPIKeyError(
                "LLM API key not configured. "
                "Set LLM_API_KEY or OPENAI_API_KEY environment variable, "
                "or pass api_key parameter."
            )

        self.model = model or settings.llm.model
        self.temperature = settings.llm.temperature
        self.max_tokens = settings.llm.max_tokens

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.llm.base_url,
        )
        logger.debug(f"LLMParser initialized with model: {self.model}")

    def _get_dynamic_prompt(self) -> str:
        """Generate system prompt with current date injected.

        Returns:
            System prompt with today's date and relative date references.
        """
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        return SYSTEM_PROMPT_TEMPLATE.format(
            today=today.isoformat(),
            yesterday=yesterday.isoformat(),
            week_ago=week_ago.isoformat(),
        )

    def _preprocess_llm_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Preprocess LLM response data before creating SearchQuery.

        Handles:
        - Converting size strings ("10MB") to bytes (int)
        - Any other data transformations needed

        Args:
            data: Raw JSON data from LLM response.

        Returns:
            Preprocessed data suitable for SearchQuery constructor.
        """
        # Convert size strings to bytes if needed
        for key in ["min_size", "max_size"]:
            if key in data and isinstance(data[key], str):
                data[key] = _parse_size(data[key])

        return data

    def parse(self, query: str) -> SearchQuery:
        """Parse natural language query to SearchQuery.

        Args:
            query: Natural language search query.

        Returns:
            Parsed SearchQuery object.

        Raises:
            LLMConnectionError: If connection to LLM fails.
            LLMParseError: If LLM cannot parse the query.
            LLMResponseError: If LLM returns invalid response.
        """
        logger.info(f"Parsing query: {query}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_dynamic_prompt()},
                    {"role": "user", "content": query},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            logger.error(f"LLM connection failed: {e}")
            raise LLMConnectionError(f"Failed to connect to LLM: {e}") from e

        content = response.choices[0].message.content
        if not content:
            raise LLMResponseError("LLM returned empty response")

        logger.debug(f"LLM response: {content}")

        try:
            # Clean up response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("\n", 1)[0]
            content = content.strip()

            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {content}")
            raise LLMParseError(f"Invalid JSON response from LLM: {e}") from e

        # Preprocess data (convert size strings to bytes, etc.)
        data = self._preprocess_llm_data(data)

        # Build SearchQuery from parsed data
        try:
            search_query = SearchQuery(**data)
            logger.info(f"Parsed query: {search_query}")
            return search_query
        except Exception as e:
            logger.error(f"Failed to create SearchQuery: {e}")
            raise LLMParseError(f"Failed to create SearchQuery: {e}") from e
