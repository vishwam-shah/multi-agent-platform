"""execute_run must be safe to re-invoke mid-run: on serverless, the background
task executing a run can be killed when its instance is recycled, and the API
resumes it by calling execute_run again. Already-completed steps must be
skipped (not redone) and their results must still be visible to later steps.
"""

import uuid
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest_asyncio.fixture
async def db_session(tmp_path, monkeypatch):
    # app.database's engine/async_session are module-level singletons bound at
    # first import, so env-var tricks after the fact won't isolate a test DB
    # from a developer's real local database. Point every module that already
    # holds a reference to app.database.async_session at a throwaway engine
    # instead.
    from app.database import Base
    import app.models.memory  # noqa: F401  (registers tables on Base.metadata)
    import app.models.run  # noqa: F401
    import app.models.step  # noqa: F401
    import app.models.trace  # noqa: F401

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/test.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    import app.agents.orchestrator as orchestrator_module

    monkeypatch.setattr(orchestrator_module, "async_session", session_factory)

    yield session_factory

    await engine.dispose()


@pytest.mark.asyncio
async def test_resume_skips_completed_steps(db_session):
    from app.models.run import Run
    from app.models.step import Step

    run_id = str(uuid.uuid4())

    async with db_session() as db:
        run = Run(
            id=run_id,
            goal="test goal",
            model_provider="openai",
            model_name="gpt-4o",
            status="running",
            plan_json=[
                {"index": 0, "description": "step 0"},
                {"index": 1, "description": "step 1"},
            ],
        )
        db.add(run)
        db.add(Step(
            id=str(uuid.uuid4()), run_id=run_id, index=0, description="step 0",
            status="completed", output_data={"result": "already done"},
        ))
        db.add(Step(id=str(uuid.uuid4()), run_id=run_id, index=1, description="step 1", status="pending"))
        await db.commit()

    calls = []

    async def fake_execute_step(description, memory_context, provider, model, tracer):
        calls.append((description, dict(memory_context)))
        return f"result for {description}"

    from app.agents import orchestrator

    with patch.object(orchestrator, "execute_step", fake_execute_step):
        await orchestrator.execute_run(run_id, "test goal", "openai", "gpt-4o")

    async with db_session() as db:
        run = (await db.execute(select(Run).where(Run.id == run_id))).scalar_one()
        steps = (
            (await db.execute(select(Step).where(Step.run_id == run_id).order_by(Step.index)))
            .scalars()
            .all()
        )

    assert len(calls) == 1, f"expected only the pending step to run, got {calls}"
    assert calls[0][0] == "step 1"
    assert "step_0_result" in calls[0][1], "completed step's result must be replayed into memory"
    assert run.status == "completed"
    assert steps[0].status == "completed"
    assert steps[1].status == "completed"
    assert steps[1].output_data["result"] == "result for step 1"
