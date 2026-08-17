from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.step import Step
from app.schemas.step import StepOut

router = APIRouter(tags=["steps"])


@router.get("/runs/{run_id}/steps", response_model=list[StepOut])
async def list_steps(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Step).where(Step.run_id == run_id).order_by(Step.index)
    )
    return result.scalars().all()


@router.get("/runs/{run_id}/steps/{step_id}", response_model=StepOut)
async def get_step(run_id: str, step_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Step).where(Step.id == step_id, Step.run_id == run_id)
    )
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return step
