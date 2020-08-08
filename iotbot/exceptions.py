class ContextTypeError(Exception):
    """不是正确的消息上下文对象"""

class InvalidConfigError(Exception):
    """配置文件有毛病"""

class InvalidPluginError(Exception):
    """插件问题"""