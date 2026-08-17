from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.trace import Trace
from app.schemas.trace import TraceOut

router = APIRouter(tags=["traces"])


@router.get("/runs/{run_id}/traces", response_model=list[TraceOut])
async def list_run_traces(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Trace).where(Trace.run_id == run_id).order_by(Trace.timestamp)
    )
    return result.scalars().all()


@router.get("/runs/{run_id}/steps/{step_id}/traces", response_model=list[TraceOut])
async def list_step_traces(
    run_id: str, step_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Trace)
        .where(Trace.run_id == run_id, Trace.step_id == step_id)
        .order_by(Trace.timestamp)
    )
    return result.scalars().all()
