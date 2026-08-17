from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory


class MemoryStore:
    def __init__(self, db: AsyncSession, run_id: str):
        self.db = db
        self.run_id = run_id

    async def write(self, key: str, value: dict):
        existing = await self.db.execute(
            select(Memory).where(Memory.run_id == self.run_id, Memory.key == key)
        )
        mem = existing.scalar_one_or_none()
        if mem:
            mem.value = value
        else:
            mem = Memory(run_id=self.run_id, key=key, value=value)
            self.db.add(mem)
        await self.db.commit()

    async def read(self, key: str) -> dict | None:
        result = await self.db.execute(
            select(Memory).where(Memory.run_id == self.run_id, Memory.key == key)
        )
        mem = result.scalar_one_or_none()
        return mem.value if mem else None

    async def read_all(self) -> dict[str, dict]:
        result = await self.db.execute(
            select(Memory).where(Memory.run_id == self.run_id)
        )
        return {m.key: m.value for m in result.scalars().all()}
