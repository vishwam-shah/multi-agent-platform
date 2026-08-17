import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.run import Run
from app.schemas.run import RunCreate, RunDetailOut, RunOut

router = APIRouter(tags=["runs"])


@router.post("/runs", response_model=RunOut, status_code=201)
async def create_run(body: RunCreate, db: AsyncSession = Depends(get_db)):
    run = Run(
        goal=body.goal,
        model_provider=body.model_provider,
        model_name=body.model_name,
        status="pending",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    from app.agents.orchestrator import execute_run

    asyncio.create_task(execute_run(run.id, run.goal, run.model_provider, run.model_name))

    return run


@router.get("/runs", response_model=list[RunOut])
async def list_runs(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Run).order_by(Run.created_at.desc()).offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/runs/{run_id}", response_model=RunDetailOut)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Run).where(Run.id == run_id).options(selectinload(Run.steps))
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.delete("/runs/{run_id}", status_code=204)
async def cancel_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Run already {run.status}")
    run.status = "cancelled"
    await db.commit()
