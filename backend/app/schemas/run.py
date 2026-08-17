from datetime import datetime
from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    goal: str = Field(..., min_length=1, max_length=2000)
    model_provider: str = Field(default="openai", pattern="^(openai|anthropic)$")
    model_name: str = Field(default="gpt-4o")


class StepOut(BaseModel):
    id: str
    index: int
    description: str
    status: str
    input_data: dict | None = None
    output_data: dict | None = None
    retries: int = 0
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cost_usd: float = 0.0
    tokens: int = 0

    model_config = {"from_attributes": True}


class RunOut(BaseModel):
    id: str
    goal: str
    model_provider: str
    model_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    plan_json: dict | None = None
    error: str | None = None
    cost_usd: float = 0.0
    tokens: int = 0

    model_config = {"from_attributes": True}


class RunDetailOut(RunOut):
    steps: list[StepOut] = []
