import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


class HourlyRotatingLogger:
    """
    专门的日志输出模块，支持按小时分割日志文件
    """

    _instance: Optional['HourlyRotatingLogger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'HourlyRotatingLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        """初始化日志配置"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 创建logger
        self._logger = logging.getLogger("aladdin")
        self._logger.setLevel(logging.DEBUG)

        # 避免重复添加handler
        if self._logger.handlers:
            return

        # 配置文件handler - 按小时轮转
        log_file = log_dir / "aladdin.log"
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when='H',  # 按小时轮转
            interval=1,  # 每1小时轮转一次
            backupCount=24*7,  # 保留7天的日志文件 (24小时 * 7天)
            encoding='utf-8'
        )

        # 配置控制台handler
        console_handler = logging.StreamHandler(sys.stdout)

        # 设置日志格式
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 设置日志级别
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.INFO)

        # 添加handler
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

        # 自定义文件名格式，添加时间戳
        file_handler.namer = self._custom_namer

    def _custom_namer(self, name: str) -> str:
        """自定义轮转文件名格式"""
        # 原始文件名格式: aladdin.log.2023-12-01_14
        # 自定义格式: aladdin_2023-12-01_14.log
        if '.' in name:
            base_name, timestamp = name.rsplit('.', 1)
            return f"{base_name.replace('.log', '')}_{timestamp}.log"
        return name

    @property
    def logger(self) -> logging.Logger:
        """获取logger实例"""
        if self._logger is None:
            self._setup_logger()
        return self._logger

    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """异常日志（包含堆栈信息）"""
        self.logger.exception(message, *args, **kwargs)


# 创建全局logger实例
logger = HourlyRotatingLogger()

# 便捷的日志函数
def log_debug(message: str, *args, **kwargs):
    """调试日志"""
    logger.debug(message, *args, **kwargs)

def log_info(message: str, *args, **kwargs):
    """信息日志"""
    logger.info(message, *args, **kwargs)

def log_warning(message: str, *args, **kwargs):
    """警告日志"""
    logger.warning(message, *args, **kwargs)

def log_error(message: str, *args, **kwargs):
    """错误日志"""
    logger.error(message, *args, **kwargs)

def log_critical(message: str, *args, **kwargs):
    """严重错误日志"""
    logger.critical(message, *args, **kwargs)

def log_exception(message: str, *args, **kwargs):
    """异常日志（包含堆栈信息）"""
    logger.exception(message, *args, **kwargs)


# 为了向后兼容，提供一个print的替代函数
def log_print(*args, sep: str = ' ', end: str = '\n', **kwargs):
    """
    替代print函数的日志输出
    将print的内容作为info级别日志输出
    """
    message = sep.join(str(arg) for arg in args) + end.rstrip('\n')
    logger.info(message)