import asyncio
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.run import Run
from app.models.trace import Trace
from app.pricing import estimate_cost
from app.schemas.run import RunCreate, RunDetailOut, RunOut

router = APIRouter(tags=["runs"])


async def _attach_costs(db: AsyncSession, runs: list[Run], include_steps: bool = False):
    """Compute live cost/token totals per run (and per step, if loaded) from trace token usage."""
    run_ids = [r.id for r in runs]
    if not run_ids:
        return

    result = await db.execute(
        select(Trace.run_id, Trace.step_id, Trace.model, Trace.token_usage).where(
            Trace.run_id.in_(run_ids)
        )
    )

    run_cost: dict[str, float] = defaultdict(float)
    run_tokens: dict[str, int] = defaultdict(int)
    step_cost: dict[str, float] = defaultdict(float)
    step_tokens: dict[str, int] = defaultdict(int)

    for run_id, step_id, model, token_usage in result.all():
        cost = estimate_cost(model, token_usage)
        tokens = (token_usage or {}).get("total_tokens", 0) or 0
        run_cost[run_id] += cost
        run_tokens[run_id] += tokens
        if step_id:
            step_cost[step_id] += cost
            step_tokens[step_id] += tokens

    for run in runs:
        run.cost_usd = round(run_cost.get(run.id, 0.0), 6)
        run.tokens = run_tokens.get(run.id, 0)
        if include_steps:
            for step in run.steps:
                step.cost_usd = round(step_cost.get(step.id, 0.0), 6)
                step.tokens = step_tokens.get(step.id, 0)


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
    runs = list(result.scalars().all())
    await _attach_costs(db, runs)
    return runs


@router.get("/runs/{run_id}", response_model=RunDetailOut)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Run).where(Run.id == run_id).options(selectinload(Run.steps))
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    await _attach_costs(db, [run], include_steps=True)
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
