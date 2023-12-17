"""the bridge config schema."""

try:
    from .auth_schema import (
        TelegramAuthResponse,
        TelegramAuthResponseSchema,
        TelegramAuthSchema,
    )
    from .base_response_schema import BaseResponse
    from .bridge_schema import BridgeResponse, BridgeResponseSchema
    from .health_schema import Health, HealthHistory, HealthHistoryManager, HealthSchema
except ImportError as ex:
    raise ex
