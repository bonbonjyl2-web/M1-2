from pydantic import BaseModel
from typing import List

class NLPAnalysisResponse(BaseModel):
    keywords: List[str]
    summary: str

    class Config:
        from_attributes = True