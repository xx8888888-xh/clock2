"""
简单日志系统
修复BUG-030: 实现基础日志功能
"""

import logging
import os
from datetime import datetime

class SimpleLogger:
    """简单日志类"""
    
    def __init__(self, name="app", log_level=logging.INFO, log_file="app.log"):
        self.name = name
        self.log_file = log_file
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建文件handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            
            # 创建控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 创建formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handler
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """错误日志"""
        self.logger.error(message)
    
    def critical(self, message):
        """严重错误日志"""
        self.logger.critical(message)
    
    def log_exception(self, exception, context=""):
        """记录异常"""
        self.error(f"{context}: {type(exception).__name__}: {exception}")
    
    @staticmethod
    def get_timestamp():
        """获取时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 全局日志实例
app_logger = SimpleLogger("clock2_app")

def setup_logging():
    """设置日志系统"""
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建多个日志器
    loggers = {
        'app': SimpleLogger('app', log_file='logs/app.log'),
        'error': SimpleLogger('error', log_level=logging.ERROR, log_file='logs/error.log'),
        'debug': SimpleLogger('debug', log_level=logging.DEBUG, log_file='logs/debug.log')
    }
    
    return loggers

def log_method_call(func):
    """方法调用日志装饰器"""
    def wrapper(*args, **kwargs):
        app_logger.info(f"调用方法: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            app_logger.info(f"方法完成: {func.__name__}")
            return result
        except Exception as e:
            app_logger.log_exception(e, f"方法失败: {func.__name__}")
            raise
    return wrapper

def log_android_operation(func):
    """Android操作日志装饰器"""
    def wrapper(*args, **kwargs):
        app_logger.info(f"Android操作: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            app_logger.info(f"Android操作完成: {func.__name__}")
            return result
        except Exception as e:
            app_logger.error(f"Android操作失败: {func.__name__} - {e}")
            return None
    return wrapper

# 导出常用函数
debug = app_logger.debug
info = app_logger.info
warning = app_logger.warning
error = app_logger.error
critical = app_logger.critical
log_exception = app_logger.log_exception