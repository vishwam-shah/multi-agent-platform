import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.agents.planner import plan_goal
from app.agents.worker import execute_step
from app.config import settings
from app.database import async_session
from app.memory.store import MemoryStore
from app.models.run import Run
from app.models.step import Step
from app.tracing.tracer import Tracer

logger = logging.getLogger(__name__)


async def execute_run(run_id: str, goal: str, provider: str, model: str):
    """Execute (or resume) a run.

    Safe to call more than once for the same run_id: on serverless deployments
    the original background task can be killed mid-run when the instance is
    recycled, so callers may re-invoke this to pick up where it left off. Work
    already committed to the DB (plan, completed steps) is skipped rather than
    redone.
    """
    async with async_session() as db:
        try:
            run = (await db.execute(select(Run).where(Run.id == run_id))).scalar_one()

            if run.status == "cancelled":
                return

            if run.plan_json is None:
                run.status = "planning"
                await db.commit()

                tracer = Tracer(db, run_id)
                plan = await plan_goal(goal, provider, model, tracer)

                run.plan_json = plan
                run.status = "running"
                await db.commit()
            else:
                plan = run.plan_json

            existing_steps = (
                (await db.execute(select(Step).where(Step.run_id == run_id).order_by(Step.index)))
                .scalars()
                .all()
            )

            if existing_steps:
                steps = list(existing_steps)
            else:
                steps = []
                for item in plan:
                    step = Step(
                        run_id=run_id,
                        index=item["index"],
                        description=item["description"],
                        status="pending",
                        input_data=item,
                    )
                    db.add(step)
                    steps.append(step)
                await db.commit()
                for s in steps:
                    await db.refresh(s)

            memory_store = MemoryStore(db, run_id)

            for step in steps:
                if step.status == "completed":
                    # Replay already-completed step results into memory so
                    # later steps resumed in a fresh invocation still see them.
                    await memory_store.write(
                        f"step_{step.index}_result",
                        {"result": (step.output_data or {}).get("result"), "description": step.description},
                    )
                    continue
                run = (await db.execute(select(Run).where(Run.id == run_id))).scalar_one()
                if run.status == "cancelled":
                    logger.info(f"Run {run_id} cancelled, stopping execution")
                    return

                step.status = "running"
                step.started_at = datetime.now(timezone.utc)
                await db.commit()

                step_tracer = Tracer(db, run_id, step.id)
                memory_context = await memory_store.read_all()

                success = False
                last_error = None

                for attempt in range(settings.max_retries + 1):
                    try:
                        result = await execute_step(
                            step.description,
                            memory_context,
                            provider,
                            model,
                            step_tracer,
                        )

                        step.output_data = {"result": result}
                        step.status = "completed"
                        step.completed_at = datetime.now(timezone.utc)
                        step.retries = attempt
                        await db.commit()

                        await memory_store.write(
                            f"step_{step.index}_result",
                            {"result": result, "description": step.description},
                        )

                        success = True
                        break

                    except Exception as e:
                        last_error = str(e)
                        logger.warning(
                            f"Step {step.index} attempt {attempt + 1} failed: {last_error}"
                        )
                        await step_tracer.log(
                            "retry",
                            input_data={"attempt": attempt + 1, "error": last_error},
                        )
                        if attempt < settings.max_retries:
                            delay = settings.retry_base_delay * (2 ** attempt)
                            await asyncio.sleep(delay)

                if not success:
                    step.status = "failed"
                    step.error = last_error
                    step.completed_at = datetime.now(timezone.utc)
                    step.retries = settings.max_retries
                    await db.commit()

                    run.status = "failed"
                    run.error = f"Step {step.index} failed after {settings.max_retries + 1} attempts: {last_error}"
                    await db.commit()
                    return

            run = (await db.execute(select(Run).where(Run.id == run_id))).scalar_one()
            if run.status == "running":
                run.status = "completed"
                await db.commit()

        except Exception as e:
            logger.exception(f"Run {run_id} failed with unexpected error")
            async with async_session() as err_db:
                run = (await err_db.execute(select(Run).where(Run.id == run_id))).scalar_one()
                run.status = "failed"
                run.error = str(e)
                await err_db.commit()
