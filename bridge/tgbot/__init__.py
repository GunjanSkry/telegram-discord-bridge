"""Initialize the telegram_handler module."""

try:
    from .core import TelegramBotHandler
except ImportError as ex:
    raise ex
