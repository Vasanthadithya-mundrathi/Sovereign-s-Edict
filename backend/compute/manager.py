"""
Compute resource manager for Sovereign's Edict
"""
from typing import List, Dict, Any
import psutil
import os
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.comment import Comment


def assess_requirements(comments: List[Comment]) -> Dict[str, Any]:
    """
    Assess computational requirements based on dataset size
    """
    num_comments = len(comments)
    
    # Simple heuristic for resource requirements
    if num_comments < 1000:
        compute_type = "local"
        memory_required = "512MB"
        processing_time = "1-2 minutes"
    elif num_comments < 10000:
        compute_type = "local"
        memory_required = "1GB"
        processing_time = "5-10 minutes"
    elif num_comments < 100000:
        compute_type = "hybrid"
        memory_required = "2GB"
        processing_time = "30-60 minutes"
    else:
        compute_type = "cloud"
        memory_required = "4GB+"
        processing_time = "2-4 hours"
    
    return {
        "num_comments": num_comments,
        "compute_type": compute_type,
        "memory_required": memory_required,
        "processing_time": processing_time,
        "recommended_action": f"Process {compute_type}"
    }


def get_system_resources() -> Dict[str, Any]:
    """
    Get current system resource availability
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        "cpu_percent": cpu_percent,
        "memory_available": memory.available,
        "memory_total": memory.total,
        "memory_percent": memory.percent
    }


def route_processing(job: Dict[str, Any]) -> str:
    """
    Route processing job to appropriate resource
    """
    requirements = job.get("requirements", {})
    compute_type = requirements.get("compute_type", "local")
    
    system_resources = get_system_resources()
    
    # If local processing is recommended and we have resources, use local
    if compute_type == "local" and system_resources["memory_percent"] < 80:
        return "local"
    
    # If hybrid is recommended, use local for preprocessing, cloud for heavy lifting
    if compute_type == "hybrid":
        return "hybrid"
    
    # Otherwise, use cloud
    return "cloud"


def optimize_resources(jobs: List[Dict]) -> Dict[str, Any]:
    """
    Optimize resource allocation for multiple jobs
    """
    # Simple optimization - process jobs in order of size
    sorted_jobs = sorted(jobs, key=lambda x: x.get("requirements", {}).get("num_comments", 0))
    
    return {
        "processing_order": [job.get("id") for job in sorted_jobs],
        "resource_allocation": "sequential"
    }