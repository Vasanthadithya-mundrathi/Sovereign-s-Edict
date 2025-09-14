"""
Citation oracle for Sovereign's Edict
"""
from typing import List, Dict
import uuid
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.citation import Citation, CitationType
from models.argument import Argument


# Sample citation database - in reality, this would be much larger
SAMPLE_CITATIONS = [
    Citation(
        id="cit_001",
        title="Puttaswamy Judgment on Privacy Rights",
        source="Supreme Court of India",
        type=CitationType.LEGAL,
        url="https://example.com/puttaswamy-judgment",
        summary="Landmark judgment establishing privacy as a fundamental right under the Indian Constitution.",
        relevance_score=0.98
    ),
    Citation(
        id="cit_002",
        title="General Data Protection Regulation (GDPR)",
        source="European Union",
        type=CitationType.LEGAL,
        url="https://example.com/gdpr",
        summary="Regulation on data protection and privacy in the European Union.",
        relevance_score=0.95
    ),
    Citation(
        id="cit_003",
        title="Economic Impact of Data Privacy Laws",
        source="Journal of Digital Economics",
        type=CitationType.ACADEMIC,
        url="https://example.com/economic-impact",
        summary="Study on the economic effects of implementing strict data privacy regulations.",
        relevance_score=0.85
    )
]


def find_citations(argument: Argument) -> List[Citation]:
    """
    Find relevant citations for an argument
    This is a simplified implementation - in reality, this would use semantic search
    """
    relevant_citations = []
    
    # Simple keyword matching - in reality, this would use embeddings and similarity search
    argument_text = argument.text.lower()
    
    for citation in SAMPLE_CITATIONS:
        citation_text = (citation.title + " " + citation.summary).lower()
        
        # Check for keyword overlap
        keywords = set(argument_text.split()) & set(citation_text.split())
        
        if len(keywords) > 2:  # Arbitrary threshold
            relevant_citations.append(citation)
    
    return relevant_citations


def validate_citation(citation_id: str) -> bool:
    """
    Validate that a citation exists in our database
    """
    return any(citation.id == citation_id for citation in SAMPLE_CITATIONS)