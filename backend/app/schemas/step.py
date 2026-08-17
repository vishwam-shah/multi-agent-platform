from datetime import datetime
from pydantic import BaseModel


class StepOut(BaseModel):
    id: str
    run_id: str
    index: int
    description: str
    status: str
    input_data: dict | None = None
    output_data: dict | None = None
    retries: int = 0
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
