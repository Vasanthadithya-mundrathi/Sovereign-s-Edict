"""
Data parser for Sovereign's Edict
"""
import pandas as pd
import json
from typing import List, Dict, Any
from datetime import datetime
import uuid
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.comment import Comment
from models.policy import PolicyDocument, PolicyClause


def parse_csv_comments(file_path: str) -> List[Comment]:
    """
    Parse comments from a CSV file
    
    Expected columns:
    - text: The comment text
    - source: Source of the comment
    - timestamp: When the comment was made
    - policy_clause: The clause the comment refers to
    - metadata: JSON string containing additional metadata
    """
    df = pd.read_csv(file_path)
    comments = []
    
    for _, row in df.iterrows():
        comment = Comment(
            id=str(uuid.uuid4()),
            text=row['text'],
            source=row['source'],
            timestamp=pd.to_datetime(row['timestamp']) if 'timestamp' in row else datetime.now(),
            policy_clause=row['policy_clause'] if 'policy_clause' in row else "unknown",
            metadata=json.loads(row['metadata']) if 'metadata' in row and pd.notna(row['metadata']) else {}
        )
        comments.append(comment)
    
    return comments


def parse_json_comments(file_path: str) -> List[Comment]:
    """
    Parse comments from a JSON file
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    comments = []
    for item in data:
        comment = Comment(
            id=item.get('id', str(uuid.uuid4())),
            text=item['text'],
            source=item.get('source', 'unknown'),
            timestamp=pd.to_datetime(item['timestamp']) if 'timestamp' in item else datetime.now(),
            policy_clause=item.get('policy_clause', 'unknown'),
            metadata=item.get('metadata', {})
        )
        comments.append(comment)
    
    return comments


def parse_policy_document(file_path: str) -> PolicyDocument:
    """
    Parse a policy document from a text file
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Simple parsing - in reality, this would be more sophisticated
    # and might use NLP to identify clauses
    clauses = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('#'):
            clause = PolicyClause(
                id=f"clause_{i:03d}",
                text=line.strip(),
                section=f"Section {i+1}",
                arguments_for=[],
                arguments_against=[]
            )
            clauses.append(clause)
    
    policy = PolicyDocument(
        id=str(uuid.uuid4()),
        title="Policy Document",
        content=content,
        clauses=clauses
    )
    
    return policy