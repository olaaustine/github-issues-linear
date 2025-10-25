from pydantic import BaseModel
from uuid import UUID


class Variables(BaseModel):
    teamId: UUID
    title: str
    description: str | None = None

    def as_input(self):
        data = self.model_dump()
        data["teamId"] = str(data["teamId"])
        return {"input": data}
