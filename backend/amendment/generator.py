"""
Amendment suggestion generator for Sovereign's Edict
"""
from typing import List, Dict, Tuple
import uuid
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.argument import Argument, ArgumentType
from models.citation import Citation
from citation.oracle import find_citations


def suggest_amendments(arguments: List[Argument]) -> List[Dict]:
    """
    Generate amendment suggestions based on arguments
    """
    # Group arguments by clause
    clause_arguments = {}
    for arg in arguments:
        if arg.clause not in clause_arguments:
            clause_arguments[arg.clause] = []
        clause_arguments[arg.clause].append(arg)
    
    suggestions = []
    
    for clause, args in clause_arguments.items():
        # Count support vs objection arguments
        support_count = sum(1 for arg in args if arg.type == ArgumentType.SUPPORT)
        objection_count = sum(1 for arg in args if arg.type == ArgumentType.OBJECTION)
        
        # Generate suggestion based on argument balance
        if objection_count > support_count:
            suggestion = generate_objection_response(clause, args)
        elif support_count > objection_count:
            suggestion = generate_support_acknowledgment(clause, args)
        else:
            suggestion = generate_balanced_review(clause, args)
        
        suggestions.append(suggestion)
    
    return suggestions


def generate_objection_response(clause: str, arguments: List[Argument]) -> Dict:
    """
    Generate a response to objections
    """
    # Find the most common themes in objections
    theme_count = {}
    for arg in arguments:
        if arg.type == ArgumentType.OBJECTION:
            for theme in arg.themes:
                theme_count[theme] = theme_count.get(theme, 0) + 1
    
    # Get top themes
    top_themes = sorted(theme_count.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Find relevant citations
    citations = []
    for arg in arguments:
        if arg.type == ArgumentType.OBJECTION:
            arg_citations = find_citations(arg)
            citations.extend(arg_citations)
    
    # Remove duplicate citations
    unique_citations = []
    seen_ids = set()
    for cit in citations:
        if cit.id not in seen_ids:
            unique_citations.append(cit)
            seen_ids.add(cit.id)
    
    return {
        "id": str(uuid.uuid4()),
        "clause": clause,
        "type": "objection_response",
        "summary": f"Address concerns regarding {', '.join([theme[0] for theme in top_themes])}",
        "details": f"This clause has received significant objection, primarily concerning {', '.join([theme[0] for theme in top_themes])}. Consider revising to address these concerns.",
        "suggested_change": f"Revise clause {clause} to better address {', '.join([theme[0] for theme in top_themes])} concerns",
        "citations": [cit.dict() for cit in unique_citations[:3]],  # Top 3 citations
        "confidence": 0.9
    }


def generate_support_acknowledgment(clause: str, arguments: List[Argument]) -> Dict:
    """
    Generate an acknowledgment of support
    """
    return {
        "id": str(uuid.uuid4()),
        "clause": clause,
        "type": "support_acknowledgment",
        "summary": "Positive reception",
        "details": "This clause has received strong support from commenters.",
        "suggested_change": "Retain this clause as currently worded",
        "citations": [],
        "confidence": 0.8
    }


def generate_balanced_review(clause: str, arguments: List[Argument]) -> Dict:
    """
    Generate a balanced review for mixed feedback
    """
    return {
        "id": str(uuid.uuid4()),
        "clause": clause,
        "type": "balanced_review",
        "summary": "Mixed feedback requires detailed review",
        "details": "This clause has received both support and objection. A detailed review is recommended.",
        "suggested_change": f"Conduct detailed review of clause {clause} considering all feedback",
        "citations": [],
        "confidence": 0.7
    }