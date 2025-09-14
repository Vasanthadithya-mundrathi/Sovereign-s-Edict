"""
Main application for Sovereign's Edict
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List, Dict
import uuid
import json
import os

from .models.comment import Comment
from .models.argument import Argument
from .models.policy import PolicyDocument
from .models.citation import Citation

from .ingestion.parser import parse_csv_comments, parse_json_comments, parse_policy_document
from .mining.extractor import extract_arguments
from .citation.oracle import find_citations
from .fusion.engine import aggregate_arguments, calculate_argument_weights
from .amendment.generator import suggest_amendments
from .compute.manager import assess_requirements, route_processing

# Import Gemini extractor
from .mining.gemini_extractor import GeminiArgumentExtractor

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

@app.post("/analyze")
async def analyze_comments():
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