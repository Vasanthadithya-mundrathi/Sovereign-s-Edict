"""
Multi-source fusion engine for Sovereign's Edict
"""
from typing import List, Dict
from collections import defaultdict
import statistics
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.argument import Argument
from models.comment import Comment


def aggregate_arguments(arguments: List[Argument]) -> Dict[str, List[Argument]]:
    """
    Aggregate arguments by clause
    """
    clause_arguments = defaultdict(list)
    
    for argument in arguments:
        clause_arguments[argument.clause].append(argument)
    
    return dict(clause_arguments)


def calculate_argument_weights(arguments: List[Argument]) -> Dict[str, float]:
    """
    Calculate weights for arguments based on confidence and source diversity
    """
    weights = {}
    
    # Group arguments by text to identify duplicates across sources
    argument_texts = defaultdict(list)
    for arg in arguments:
        argument_texts[arg.text].append(arg)
    
    for arg_text, arg_list in argument_texts.items():
        # Weight based on average confidence and number of sources
        avg_confidence = statistics.mean([arg.confidence for arg in arg_list])
        source_diversity = len(set(arg.comment_id for arg in arg_list))
        
        # Calculate weight (simple formula - can be more sophisticated)
        weight = avg_confidence * (1 + source_diversity * 0.1)
        
        # Assign weight to all arguments with this text
        for arg in arg_list:
            weights[arg.id] = weight
    
    return weights


def detect_echo_chambers(arguments: List[Argument]) -> List[str]:
    """
    Detect potential echo chambers (arguments that appear too frequently from similar sources)
    """
    # This is a simplified implementation
    # In reality, this would analyze source diversity and correlation
    
    argument_sources = defaultdict(set)
    for arg in arguments:
        argument_sources[arg.text].add(arg.comment_id)
    
    # Arguments with too many similar sources might be echo chambers
    echo_chambers = []
    for arg_text, sources in argument_sources.items():
        if len(sources) > 10:  # Arbitrary threshold
            # Find arguments with this text
            for arg in arguments:
                if arg.text == arg_text:
                    echo_chambers.append(arg.id)
    
    return echo_chambers


def cross_validate_arguments(arguments: List[Argument]) -> Dict[str, bool]:
    """
    Cross-validate arguments across multiple sources
    """
    validation_results = {}
    
    # Group arguments by text
    argument_texts = defaultdict(list)
    for arg in arguments:
        argument_texts[arg.text].append(arg)
    
    for arg_text, arg_list in argument_texts.items():
        # Consider validated if it appears in multiple sources
        is_validated = len(arg_list) > 1
        
        # Assign validation result to all arguments with this text
        for arg in arg_list:
            validation_results[arg.id] = is_validated
    
    return validation_results