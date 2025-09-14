"""
Comment data model for Sovereign's Edict
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class Comment(BaseModel):
    """
    Represents a single comment on a policy document
    """
    id: str
    text: str
    source: str
    timestamp: datetime
    policy_clause: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "comment_001",
                "text": "This clause seems to infringe on individual privacy rights.",
                "source": "e-consultation_portal",
                "timestamp": "2023-01-15T10:30:00Z",
                "policy_clause": "Section 7(a)",
                "metadata": {
                    "author": "Anonymous",
                    "location": "Delhi",
                    "category": "privacy"
                }
            }
        }