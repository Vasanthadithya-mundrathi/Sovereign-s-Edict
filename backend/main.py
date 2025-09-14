"""
Main application for Sovereign's Edict
"""
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List, Dict
import uuid
import json
from datetime import datetime
from dateutil import parser

# Use absolute imports
from backend.models.comment import Comment
from backend.models.argument import Argument
from backend.models.policy import PolicyDocument
from backend.models.citation import Citation

from backend.ingestion.parser import parse_csv_comments, parse_json_comments, parse_policy_document
from backend.mining.extractor import extract_arguments
from backend.citation.oracle import find_citations
from backend.fusion.engine import aggregate_arguments, calculate_argument_weights
from backend.amendment.generator import suggest_amendments
from backend.compute.manager import assess_requirements, route_processing

# Import Gemini extractor
from backend.mining.gemini_extractor import GeminiArgumentExtractor

# Import plugin system
from backend.plugins import plugin_manager, initialize_plugins

app = FastAPI(
    title="Sovereign's Edict",
    description="An Actionable Intelligence Platform for Clause-Level Policy Argumentation",
    version="0.1.0"
)

# In-memory storage for demo purposes
# In a production system, this would be a proper database
stored_data = {
    "comments": [],
    "arguments": [],
    "policies": [],
    "citations": []
}

# Initialize plugins when the app starts
@app.on_event("startup")
async def startup_event():
    initialize_plugins()

@app.get("/")
async def root():
    return {"message": "Welcome to Sovereign's Edict API"}

@app.post("/upload/comments/csv")
async def upload_csv_comments(file: UploadFile = File(...)):
    """
    Upload comments in CSV format
    """
    try:
        # Save file temporarily
        temp_file_path = f"/tmp/{uuid.uuid4()}.csv"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse comments
        comments = parse_csv_comments(temp_file_path)
        stored_data["comments"].extend(comments)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": f"Successfully uploaded {len(comments)} comments",
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload/comments/json")
async def upload_json_comments(file: UploadFile = File(...)):
    """
    Upload comments in JSON format
    """
    try:
        # Save file temporarily
        temp_file_path = f"/tmp/{uuid.uuid4()}.json"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse comments
        comments = parse_json_comments(temp_file_path)
        stored_data["comments"].extend(comments)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": f"Successfully uploaded {len(comments)} comments",
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload/policy")
async def upload_policy_document(file: UploadFile = File(...)):
    """
    Upload policy document
    """
    try:
        # Save file temporarily
        temp_file_path = f"/tmp/{uuid.uuid4()}.txt"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse policy document
        policy = parse_policy_document(temp_file_path)
        stored_data["policies"].append(policy)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": "Successfully uploaded policy document",
            "policy_id": policy.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ingest/plugin/{plugin_name}")
async def ingest_with_plugin(plugin_name: str, source: str, source_type: str = "auto", gemini_key: str = None):
    """
    Ingest data using a specific plugin
    """
    try:
        # Store the Gemini API key for later use in analysis
        if gemini_key:
            stored_data["gemini_key"] = gemini_key
        
        # Get the module registry from the plugin manager
        module_registry = plugin_manager.module_registry
        
        # Get the ingestor plugin
        ingestor = module_registry.get_ingestor(plugin_name)
        
        if not ingestor:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found or not an ingestor")
        
        # Check if the plugin can handle this source type
        # Extract source type from the source URL for better matching if not explicitly provided
        if source_type == "auto":
            if "youtube.com" in source or "youtu.be" in source:
                source_type = "youtube"
            elif "instagram.com" in source:
                source_type = "instagram"
            elif "linkedin.com" in source:
                source_type = "linkedin"
            elif "default" in source.lower():
                source_type = "indian_legal"
            else:
                # If auto-detection didn't work, use plugin name
                source_type = plugin_name
        
        if not ingestor.can_handle(source_type):
            raise HTTPException(status_code=400, detail=f"Plugin '{plugin_name}' cannot handle this source type")
        
        # Ingest the data
        data = ingestor.ingest(source)
        
        # Convert to Comment objects
        comments = []
        for item in data:
            # Handle timestamp conversion
            timestamp_str = item.get("timestamp", "2023-01-01T00:00:00Z")
            try:
                # If it's already a datetime object, use it as is
                if isinstance(timestamp_str, datetime):
                    timestamp = timestamp_str
                else:
                    # Try to parse the timestamp string
                    # Handle various timestamp formats
                    if not timestamp_str or timestamp_str == '':
                        timestamp = datetime.now()
                    else:
                        # Try common timestamp formats
                        from dateutil import parser
                        timestamp = parser.parse(timestamp_str)
            except Exception:
                # Fallback to current time if parsing fails
                timestamp = datetime.now()
            
            comment = Comment(
                id=str(uuid.uuid4()),
                text=item.get("text", ""),
                source=item.get("source", "plugin"),
                timestamp=timestamp,
                policy_clause=item.get("metadata", {}).get("category", "general")
            )
            comments.append(comment)
        
        # Store the comments
        stored_data["comments"].extend(comments)
        
        return {
            "message": f"Successfully ingested {len(comments)} comments using {plugin_name} plugin",
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/plugins")
async def list_plugins():
    """
    List all available plugins
    """
    # Get the module registry from the plugin manager
    module_registry = plugin_manager.module_registry
    
    ingestors = module_registry.get_all_ingestors()
    processors = module_registry.get_all_processors()
    exporters = module_registry.get_all_exporters()
    
    return {
        "ingestors": list(ingestors.keys()),
        "processors": list(processors.keys()),
        "exporters": list(exporters.keys())
    }

@app.post("/analyze")
async def analyze_comments(gemini_key: str = None):
    """
    Analyze uploaded comments and generate insights
    """
    if not stored_data["comments"]:
        raise HTTPException(status_code=400, detail="No comments uploaded")
    
    if not stored_data["policies"]:
        raise HTTPException(status_code=400, detail="No policy document uploaded")
    
    # Assess computational requirements
    requirements = assess_requirements(stored_data["comments"])
    
    # Route processing
    compute_route = route_processing({"requirements": requirements})
    
    # Extract arguments using Gemini API
    try:
        # Use provided API key, then stored key, then environment variable
        api_key = gemini_key or stored_data.get("gemini_key") or os.environ.get("GEMINI_API_KEY")
        if api_key:
            extractor = GeminiArgumentExtractor(api_key=api_key)
        else:
            extractor = GeminiArgumentExtractor()
        arguments = extractor.extract_arguments(stored_data["comments"])
        stored_data["arguments"] = arguments
    except Exception as e:
        # Fallback to basic extractor if Gemini fails
        arguments = extract_arguments(stored_data["comments"])
        stored_data["arguments"] = arguments
    
    # Find citations for arguments
    for argument in arguments:
        citations = find_citations(argument)
        argument.citations = [citation.id for citation in citations]
        stored_data["citations"].extend(citations)
    
    # Calculate argument weights
    weights = calculate_argument_weights(arguments)
    
    # Aggregate arguments by clause
    clause_arguments = aggregate_arguments(arguments)
    
    # Generate amendment suggestions
    suggestions = suggest_amendments(arguments)
    
    return {
        "message": "Analysis complete",
        "requirements": requirements,
        "compute_route": compute_route,
        "num_arguments": len(arguments),
        "clause_arguments": {clause: len(args) for clause, args in clause_arguments.items()},
        "suggestions": suggestions
    }

@app.get("/results/arguments")
async def get_arguments():
    """
    Get extracted arguments
    """
    return stored_data["arguments"]

@app.get("/results/clause/{clause_id}")
async def get_clause_analysis(clause_id: str):
    """
    Get analysis for a specific clause
    """
    clause_arguments = [arg for arg in stored_data["arguments"] if arg.clause == clause_id]
    
    if not clause_arguments:
        raise HTTPException(status_code=404, detail="Clause not found")
    
    # Aggregate by theme
    theme_arguments = {}
    for arg in clause_arguments:
        for theme in arg.themes:
            if theme not in theme_arguments:
                theme_arguments[theme] = []
            theme_arguments[theme].append(arg)
    
    return {
        "clause_id": clause_id,
        "total_arguments": len(clause_arguments),
        "themes": theme_arguments,
        "support_count": len([arg for arg in clause_arguments if arg.type == "support"]),
        "objection_count": len([arg for arg in clause_arguments if arg.type == "objection"])
    }

@app.get("/results/suggestions")
async def get_amendment_suggestions():
    """
    Get amendment suggestions
    """
    if not stored_data["arguments"]:
        raise HTTPException(status_code=400, detail="No analysis completed")
    
    suggestions = suggest_amendments(stored_data["arguments"])
    return suggestions

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)