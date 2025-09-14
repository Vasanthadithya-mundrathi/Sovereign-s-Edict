"""
Tests for data models
"""
import pytest
from datetime import datetime
from ..models.comment import Comment
from ..models.argument import Argument, ArgumentType
from ..models.citation import Citation, CitationType
from ..models.policy import PolicyDocument, PolicyClause


def test_comment_model():
    """Test Comment model creation"""
    comment = Comment(
        id="test_001",
        text="This is a test comment",
        source="test_source",
        timestamp=datetime.now(),
        policy_clause="Section 1"
    )
    
    assert comment.id == "test_001"
    assert comment.text == "This is a test comment"
    assert comment.source == "test_source"
    assert comment.policy_clause == "Section 1"


def test_argument_model():
    """Test Argument model creation"""
    argument = Argument(
        id="arg_001",
        comment_id="comment_001",
        text="This is a test argument",
        type=ArgumentType.SUPPORT,
        themes=["test", "example"],
        clause="Section 1",
        confidence=0.95
    )
    
    assert argument.id == "arg_001"
    assert argument.type == ArgumentType.SUPPORT
    assert "test" in argument.themes
    assert argument.confidence == 0.95


def test_citation_model():
    """Test Citation model creation"""
    citation = Citation(
        id="cit_001",
        title="Test Citation",
        source="Test Source",
        type=CitationType.LEGAL,
        summary="This is a test citation",
        relevance_score=0.9
    )
    
    assert citation.id == "cit_001"
    assert citation.type == CitationType.LEGAL
    assert citation.relevance_score == 0.9


def test_policy_model():
    """Test PolicyDocument model creation"""
    clause = PolicyClause(
        id="clause_001",
        text="This is a test clause",
        section="Section 1"
    )
    
    policy = PolicyDocument(
        id="policy_001",
        title="Test Policy",
        content="This is a test policy document",
        clauses=[clause]
    )
    
    assert policy.id == "policy_001"
    assert policy.title == "Test Policy"
    assert len(policy.clauses) == 1
    assert policy.clauses[0].id == "clause_001"