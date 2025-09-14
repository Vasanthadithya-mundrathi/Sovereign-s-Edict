"""
Policy document data model for Sovereign's Edict
"""
from pydantic import BaseModel
from typing import List, Optional


class PolicyClause(BaseModel):
    """
    Represents a single clause in a policy document
    """
    id: str
    text: str
    section: str
    arguments_for: List[str] = []
    arguments_against: List[str] = []


class PolicyDocument(BaseModel):
    """
    Represents a complete policy document
    """
    id: str
    title: str
    content: str
    clauses: List[PolicyClause] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": "policy_001",
                "title": "Digital Privacy Protection Act",
                "content": "Full text of the policy document...",
                "clauses": [
                    {
                        "id": "clause_001",
                        "text": "All digital service providers must collect user consent before processing personal data.",
                        "section": "Section 7(a)",
                        "arguments_for": ["arg_001", "arg_002"],
                        "arguments_against": ["arg_003"]
                    }
                ]
            }
        }