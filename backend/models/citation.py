"""
Citation data model for Sovereign's Edict
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CitationType(str, Enum):
    LEGAL = "legal"
    ACADEMIC = "academic"
    EXPERT = "expert"


class Citation(BaseModel):
    """
    Represents a legal or academic citation
    """
    id: str
    title: str
    source: str
    type: CitationType
    url: Optional[str] = None
    summary: str
    relevance_score: float
    
    class Config:
        schema_extra = {
            "example": {
                "id": "cit_001",
                "title": "Puttaswamy Judgment on Privacy Rights",
                "source": "Supreme Court of India",
                "type": "legal",
                "url": "https://example.com/puttaswamy-judgment",
                "summary": "Landmark judgment establishing privacy as a fundamental right under the Indian Constitution.",
                "relevance_score": 0.98
            }
        }