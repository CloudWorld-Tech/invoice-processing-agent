from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SSEEventType(str, Enum):
    RUN_STARTED = "run_started"
    PROGRESS = "progress"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    INVOICE_RESULT = "invoice_result"
    FINAL_RESULT = "final_result"
    ERROR = "error"


class SSEEvent(BaseModel):
    event: SSEEventType
    run_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None
