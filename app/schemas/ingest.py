from pydantic import BaseModel, Field

class SampleIngestRequest(BaseModel):
    project_id: int | None = Field(default=None)