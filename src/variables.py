from pydantic import BaseModel
from uuid import UUID


class Variables(BaseModel):
    teamId: UUID
    title: str
    description: str | None = None

    def as_input(self):
        return {
            "input": {
                "teamId": str(self.teamId),
                "title": self.title,
                "description": self.description,
            }
        }
