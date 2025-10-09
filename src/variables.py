from pydantic import BaseModel


class Variables(BaseModel):
    teamId: str
    title: str
    description: str | None = None

    def as_input(self):
        return {"input": self.dict()}
