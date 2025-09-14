"""
Argument extractor for Sovereign's Edict
"""
from typing import List, Dict
import re
import uuid
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.comment import Comment
from models.argument import Argument, ArgumentType


def preprocess_text(text: str) -> str:
    """
    Preprocess text by cleaning and normalizing
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    return text.strip()


def extract_arguments(comments: List[Comment]) -> List[Argument]:
    """
    Extract arguments from comments
    This is a simplified implementation - in reality, this would use an LLM
    """
    arguments = []
    
    for comment in comments:
        processed_text = preprocess_text(comment.text)
        
        # Simple keyword-based argument detection
        # In reality, this would use a trained model
        argument_type = detect_argument_type(processed_text)
        themes = extract_themes(processed_text)
        
        argument = Argument(
            id=str(uuid.uuid4()),
            comment_id=comment.id,
            text=processed_text,
            type=argument_type,
            themes=themes,
            clause=comment.policy_clause,
            confidence=0.85  # Placeholder confidence score
        )
        
        arguments.append(argument)
    
    return arguments


def detect_argument_type(text: str) -> ArgumentType:
    """
    Detect the type of argument (support, objection, neutral)
    This is a simplified implementation
    """
    support_keywords = ['support', 'agree', 'good', 'benefit', 'positive', 'favor']
    objection_keywords = ['against', 'disagree', 'bad', 'negative', 'concern', 'problem', 'issue']
    
    text_lower = text.lower()
    
    support_count = sum(1 for keyword in support_keywords if keyword in text_lower)
    objection_count = sum(1 for keyword in objection_keywords if keyword in text_lower)
    
    if support_count > objection_count:
        return ArgumentType.SUPPORT
    elif objection_count > support_count:
        return ArgumentType.OBJECTION
    else:
        return ArgumentType.NEUTRAL


def extract_themes(text: str) -> List[str]:
    """
    Extract themes from text
    This is a simplified implementation
    """
    themes = []
    
    # Theme keywords
    theme_keywords = {
        'privacy': ['privacy', 'personal data', 'surveillance', 'monitoring'],
        'economic': ['cost', 'expense', 'money', 'financial', 'economy'],
        'legal': ['law', 'legal', 'constitution', 'rights'],
        'technical': ['technology', 'technical', 'system', 'software'],
        'implementation': ['implement', 'process', 'procedure', 'execute']
    }
    
    text_lower = text.lower()
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    # If no themes found, return neutral
    if not themes:
        themes = ['general']
    
    return themes