from pydantic import BaseModel, Field, ConfigDict

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=255)

class TodoResponse(TodoCreate):
    id: int
    complete: bool

    model_config = ConfigDict(from_attributes=True)

class TodoUpdate(TodoCreate):
    complete: bool | None = False

class TodoComplete(BaseModel):
    complete: bool | None = True