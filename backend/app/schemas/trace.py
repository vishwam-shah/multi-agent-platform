from datetime import datetime
from pydantic import BaseModel


class TraceOut(BaseModel):
    id: str
    run_id: str
    step_id: str | None = None
    event_type: str
    provider: str | None = None
    model: str | None = None
    input_data: dict | None = None
    output_data: dict | None = None
    token_usage: dict | None = None
    duration_ms: int | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}
