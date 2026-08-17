import time
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import Trace


class Tracer:
    def __init__(self, db: AsyncSession, run_id: str, step_id: str | None = None):
        self.db = db
        self.run_id = run_id
        self.step_id = step_id

    async def log(
        self,
        event_type: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        input_data: dict | None = None,
        output_data: dict | None = None,
        token_usage: dict | None = None,
        duration_ms: int | None = None,
    ):
        trace = Trace(
            run_id=self.run_id,
            step_id=self.step_id,
            event_type=event_type,
            provider=provider,
            model=model,
            input_data=input_data,
            output_data=output_data,
            token_usage=token_usage,
            duration_ms=duration_ms,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(trace)
        await self.db.commit()

    def timer(self):
        return _Timer()


class _Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = int((time.perf_counter() - self.start) * 1000)
