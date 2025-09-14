"""
Argument data model for Sovereign's Edict
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class ArgumentType(str, Enum):
    SUPPORT = "support"
    OBJECTION = "objection"
    NEUTRAL = "neutral"


class Argument(BaseModel):
    """
    Represents an extracted argument from a comment
    """
    id: str
    comment_id: str
    text: str
    type: ArgumentType
    themes: List[str]
    clause: str
    confidence: float
    citations: List[str] = []
    related_arguments: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": "arg_001",
                "comment_id": "comment_001",
                "text": "This clause infringes on individual privacy rights without sufficient justification.",
                "type": "objection",
                "themes": ["privacy", "civil_rights"],
                "clause": "Section 7(a)",
                "confidence": 0.95,
                "citations": ["cit_001", "cit_002"],
                "related_arguments": ["arg_002", "arg_003"]
            }
        }