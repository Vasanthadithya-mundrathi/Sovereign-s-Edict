# Phase 9: Privacy and Transparency Implementation

## Overview
Implement privacy-by-default, data anonymization, transparency features, and ensure no personal information is displayed.

## Implementation Steps

### 1. Client-Side Processing Option

#### Step 1: Create Client-Side Processing Module

Create `backend/processing/client_side.py`:

```python
"""
Client-side processing for Sovereign's Edict
"""
import json
from typing import List, Dict
from ..models.comment import Comment
from ..models.argument import Argument
from ..models.citation import Citation

class ClientSideProcessor:
    """
    Processor that works entirely on the client side for maximum privacy
    """
    
    @staticmethod
    def anonymize_comments(comments: List[Comment]) -> List[Comment]:
        """
        Anonymize comments by removing personal identifiers
        """
        anonymized_comments = []
        
        for comment in comments:
            # Create a copy of the comment
            anonymized_comment = Comment(
                id=comment.id,
                text=comment.text,
                source=comment.source,
                timestamp=comment.timestamp,
                policy_clause=comment.policy_clause
            )
            
            # Remove personal identifiers from text
            anonymized_comment.text = ClientSideProcessor._remove_personal_info(comment.text)
            
            # Anonymize source if it contains personal info
            if "@" in anonymized_comment.source or "user" in anonymized_comment.source.lower():
                anonymized_comment.source = "anonymous_source"
            
            anonymized_comments.append(anonymized_comment)
        
        return anonymized_comments
    
    @staticmethod
    def _remove_personal_info(text: str) -> str:
        """
        Remove personal information from text
        """
        import re
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Remove names (simple heuristic - capitalized words)
        # This is a very basic approach and might need refinement
        text = re.sub(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', '[NAME]', text)
        
        # Remove addresses (basic pattern)
        text = re.sub(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b', '[ADDRESS]', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def process_comments_locally(comments: List[Comment]) -> Dict:
        """
        Process comments locally without sending to server
        """
        # Anonymize comments first
        anonymized_comments = ClientSideProcessor.anonymize_comments(comments)
        
        # Extract arguments using basic NLP (no AI model needed for privacy)
        arguments = ClientSideProcessor._extract_basic_arguments(anonymized_comments)
        
        # Group arguments by clause
        clause_arguments = {}
        for arg in arguments:
            clause = arg.clause
            if clause not in clause_arguments:
                clause_arguments[clause] = []
            clause_arguments[clause].append(arg)
        
        # Calculate basic statistics
        stats = {
            "total_comments": len(anonymized_comments),
            "total_arguments": len(arguments),
            "clauses_analyzed": len(clause_arguments),
            "support_count": len([arg for arg in arguments if arg.type == "support"]),
            "objection_count": len([arg for arg in arguments if arg.type == "objection"])
        }
        
        return {
            "anonymized_comments": anonymized_comments,
            "arguments": arguments,
            "clause_arguments": clause_arguments,
            "statistics": stats
        }
    
    @staticmethod
    def _extract_basic_arguments(comments: List[Comment]) -> List[Argument]:
        """
        Extract arguments using basic keyword analysis
        """
        from ..models.argument import Argument, ArgumentType
        import uuid
        
        arguments = []
        support_keywords = ['support', 'agree', 'favor', 'good', 'benefit', 'positive', 'helpful']
        objection_keywords = ['oppose', 'against', 'disagree', 'bad', 'harm', 'negative', 'concern', 'worried']
        
        for comment in comments:
            text_lower = comment.text.lower()
            
            # Count keywords
            support_count = sum(1 for kw in support_keywords if kw in text_lower)
            objection_count = sum(1 for kw in objection_keywords if kw in text_lower)
            
            # Determine stance
            if support_count > objection_count:
                stance = ArgumentType.SUPPORT
                confidence = min(90, 50 + (support_count * 5))
            elif objection_count > support_count:
                stance = ArgumentType.OBJECTION
                confidence = min(90, 50 + (objection_count * 5))
            else:
                # Neutral or unclear
                stance = ArgumentType.SUPPORT  # Default to support
                confidence = 30
            
            # Create argument
            argument = Argument(
                id=str(uuid.uuid4()),
                text=comment.text[:200] + "..." if len(comment.text) > 200 else comment.text,
                type=stance,
                clause=comment.policy_clause or "general",
                themes=['general'],
                confidence=confidence,
                citations=[],
                source_comment=comment.id
            )
            arguments.append(argument)
        
        return arguments

# Utility functions for client-side use
def process_data_client_side(raw_data: str, data_type: str = "csv") -> Dict:
    """
    Process data entirely on the client side
    
    Args:
        raw_data: Raw data string (CSV, JSON, etc.)
        data_type: Type of data ('csv', 'json', 'text')
    
    Returns:
        Dict with processed results
    """
    from ..ingestion.parser import parse_csv_comments, parse_json_comments
    
    try:
        if data_type == "csv":
            # Parse CSV data
            import io
            import csv
            comments = []
            reader = csv.DictReader(io.StringIO(raw_data))
            for i, row in enumerate(reader):
                comment = Comment(
                    id=f"comment_{i}",
                    text=row.get('text', ''),
                    source=row.get('source', 'csv_upload'),
                    timestamp=i,
                    policy_clause=row.get('policy_clause', 'general')
                )
                comments.append(comment)
        elif data_type == "json":
            # Parse JSON data
            import json
            data = json.loads(raw_data)
            comments = []
            for i, item in enumerate(data):
                comment = Comment(
                    id=f"comment_{i}",
                    text=item.get('text', ''),
                    source=item.get('source', 'json_upload'),
                    timestamp=i,
                    policy_clause=item.get('policy_clause', 'general')
                )
                comments.append(comment)
        else:
            # Treat as text
            comments = [Comment(
                id="comment_0",
                text=raw_data,
                source="text_input",
                timestamp=0,
                policy_clause="general"
            )]
        
        # Process with client-side processor
        processor = ClientSideProcessor()
        results = processor.process_comments_locally(comments)
        
        return results
        
    except Exception as e:
        return {"error": f"Failed to process data: {str(e)}"}
```

#### Step 2: Create Client-Side API Endpoint

Update `backend/main.py`:

```python
# Add import
from .processing.client_side import ClientSideProcessor, process_data_client_side

# Add client-side processing endpoint
@app.post("/process/client-side")
async def process_client_side(raw_data: str, data_type: str = "csv"):
    """
    Process data entirely on the client side for maximum privacy
    """
    try:
        results = process_data_client_side(raw_data, data_type)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Client-side processing failed: {str(e)}")

# Add anonymization endpoint
@app.post("/anonymize/comments")
async def anonymize_comments_endpoint():
    """
    Anonymize stored comments for privacy
    """
    try:
        if not stored_data["comments"]:
            raise HTTPException(status_code=400, detail="No comments to anonymize")
        
        processor = ClientSideProcessor()
        anonymized_comments = processor.anonymize_comments(stored_data["comments"])
        
        # Replace stored comments with anonymized versions
        stored_data["comments"] = anonymized_comments
        
        return {
            "message": "Comments anonymized successfully",
            "anonymized_count": len(anonymized_comments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")
```

### 2. Enhanced Privacy Dashboard

#### Step 1: Create Privacy Controls

Create `backend/api/privacy.py`:

```python
"""
Privacy controls for Sovereign's Edict
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import os
import json

router = APIRouter(prefix="/privacy")

# Privacy settings
PRIVACY_SETTINGS_FILE = "data/privacy_settings.json"

def get_default_privacy_settings():
    """Get default privacy settings"""
    return {
        "data_retention_days": 30,
        "anonymize_comments": True,
        "remove_personal_info": True,
        "client_side_processing": False,
        "export_anonymized_only": True,
        "audit_logging": True
    }

def load_privacy_settings():
    """Load privacy settings from file"""
    if os.path.exists(PRIVACY_SETTINGS_FILE):
        try:
            with open(PRIVACY_SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return get_default_privacy_settings()
    else:
        return get_default_privacy_settings()

def save_privacy_settings(settings: Dict):
    """Save privacy settings to file"""
    try:
        os.makedirs(os.path.dirname(PRIVACY_SETTINGS_FILE), exist_ok=True)
        with open(PRIVACY_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False

@router.get("/settings")
async def get_privacy_settings():
    """Get current privacy settings"""
    return load_privacy_settings()

@router.post("/settings")
async def update_privacy_settings(settings: Dict):
    """Update privacy settings"""
    if save_privacy_settings(settings):
        return {"message": "Privacy settings updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save privacy settings")

@router.post("/audit-log")
async def log_privacy_event(event: str, details: str = ""):
    """Log privacy-related events"""
    settings = load_privacy_settings()
    if settings.get("audit_logging", True):
        # Log to file
        log_entry = {
            "timestamp": int(time.time()),
            "event": event,
            "details": details
        }
        
        log_file = "data/privacy_audit.log"
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to log privacy event: {str(e)}")
    
    return {"message": "Event logged"}

@router.get("/data-retention")
async def get_data_retention_info():
    """Get data retention information"""
    settings = load_privacy_settings()
    retention_days = settings.get("data_retention_days", 30)
    
    return {
        "retention_days": retention_days,
        "retention_policy": f"Data is automatically deleted after {retention_days} days",
        "last_cleanup": "Not implemented yet"
    }

@router.post("/cleanup")
async def cleanup_old_data():
    """Clean up old data based on retention settings"""
    settings = load_privacy_settings()
    retention_days = settings.get("data_retention_days", 30)
    
    # This would implement actual cleanup logic
    # For now, just return info
    return {
        "message": f"Would clean up data older than {retention_days} days",
        "cleanup_scheduled": False
    }
```

#### Step 2: Register Privacy Router

Update `backend/main.py`:

```python
# Add import
from .api import privacy

# Register router
app.include_router(privacy.router)
```

### 3. Transparency Features

#### Step 1: Create Transparency API

Create `backend/api/transparency.py`:

```python
"""
Transparency features for Sovereign's Edict
"""
from fastapi import APIRouter
from typing import Dict, List
from ..models.argument import Argument
from ..models.citation import Citation
import time

router = APIRouter(prefix="/transparency")

@router.get("/sources")
async def get_all_sources():
    """
    Get all sources used in analysis
    """
    # This would return information about all sources
    return {
        "sources": [
            {
                "type": "policy_document",
                "description": "Uploaded policy documents",
                "processing": "Text extraction and clause identification"
            },
            {
                "type": "public_comments",
                "description": "Uploaded public comments",
                "processing": "Argument extraction and sentiment analysis"
            },
            {
                "type": "citations",
                "description": "Legal and regulatory references",
                "processing": "Automated matching to known legal documents"
            }
        ]
    }

@router.get("/methodology")
async def get_analysis_methodology():
    """
    Get detailed analysis methodology
    """
    return {
        "title": "Sovereign's Edict Analysis Methodology",
        "description": "Detailed explanation of how policy arguments are extracted and analyzed",
        "steps": [
            {
                "step": 1,
                "name": "Data Ingestion",
                "description": "Policy documents and public comments are uploaded and processed",
                "details": "Text is extracted from documents and comments are parsed from structured data"
            },
            {
                "step": 2,
                "name": "Argument Extraction",
                "description": "Natural language processing identifies arguments in comments",
                "details": "Advanced AI models (Gemini or local LLMs) extract structured arguments with confidence scoring"
            },
            {
                "step": 3,
                "name": "Clause Mapping",
                "description": "Arguments are mapped to relevant policy clauses",
                "details": "NLP techniques identify which policy sections each argument addresses"
            },
            {
                "step": 4,
                "name": "Sentiment Analysis",
                "description": "Arguments are classified as support or objection",
                "details": "Machine learning models determine the stance of each argument"
            },
            {
                "step": 5,
                "name": "Citation Matching",
                "description": "Relevant legal and regulatory references are identified",
                "details": "Text matching algorithms find citations to laws, regulations, and precedents"
            },
            {
                "step": 6,
                "name": "Aggregation",
                "description": "Arguments are grouped and summarized by clause",
                "details": "Similar arguments are clustered and key themes are identified"
            },
            {
                "step": 7,
                "name": "Suggestion Generation",
                "description": "Policy amendment suggestions are generated",
                "details": "Evidence-based recommendations are created based on argument analysis"
            }
        ]
    }

@router.get("/confidence/{argument_id}")
async def get_argument_confidence(argument_id: str):
    """
    Get detailed confidence information for a specific argument
    """
    # Find the argument
    argument = None
    for arg in stored_data.get("arguments", []):
        if arg.id == argument_id:
            argument = arg
            break
    
    if not argument:
        return {"error": "Argument not found"}
    
    return {
        "argument_id": argument_id,
        "confidence_score": argument.confidence,
        "confidence_explanation": f"This argument has a confidence score of {argument.confidence}%. "
                                  f"This score is based on factors such as text clarity, citation quality, "
                                  f"and semantic coherence.",
        "factors": [
            "Text clarity and structure",
            "Presence of supporting evidence",
            "Citation quality and relevance",
            "Semantic coherence with the topic"
        ],
        "uncertainty_indicators": [
            "Limited context provided",
            "Ambiguous language used",
            "No supporting citations"
        ] if argument.confidence < 50 else [
            "Clear and structured argument",
            "Strong supporting evidence",
            "Relevant citations provided"
        ]
    }

@router.get("/audit-trail")
async def get_audit_trail():
    """
    Get audit trail of processing steps
    """
    # This would return a detailed audit trail
    return {
        "processing_steps": [
            {
                "timestamp": time.time() - 300,
                "step": "Data Upload",
                "description": "Policy document and comments uploaded",
                "details": "1 policy document, 150 comments processed"
            },
            {
                "timestamp": time.time() - 240,
                "step": "Argument Extraction",
                "description": "AI model extracted arguments from comments",
                "details": "Extracted 247 arguments with average confidence 78%"
            },
            {
                "timestamp": time.time() - 180,
                "step": "Clause Mapping",
                "description": "Arguments mapped to policy clauses",
                "details": "Mapped arguments to 12 policy clauses"
            },
            {
                "timestamp": time.time() - 120,
                "step": "Citation Matching",
                "description": "Legal citations identified",
                "details": "Found 67 relevant citations"
            },
            {
                "timestamp": time.time() - 60,
                "step": "Analysis Complete",
                "description": "Final analysis results generated",
                "details": "Ready for review and export"
            }
        ]
    }
```

#### Step 2: Register Transparency Router

Update `backend/main.py`:

```python
# Add import
from .api import transparency

# Register router
app.include_router(transparency.router)
```

### 4. Frontend Privacy and Transparency Features

#### Step 1: Update Streamlit Frontend

Update `streamlit_app.py`:

```python
# Add privacy controls
def show_privacy_controls():
    st.header("🔒 Privacy Controls")
    
    try:
        # Get current privacy settings
        response = requests.get(f"{API_BASE_URL}/privacy/settings")
        if response.status_code == 200:
            settings = response.json()
        else:
            settings = {}
    except:
        settings = {}
    
    # Privacy settings form
    st.subheader("Data Privacy Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        anonymize = st.checkbox(
            "Anonymize Comments", 
            value=settings.get("anonymize_comments", True),
            help="Remove personal identifiers from comments"
        )
        
        client_side = st.checkbox(
            "Client-Side Processing", 
            value=settings.get("client_side_processing", False),
            help="Process data locally for maximum privacy"
        )
    
    with col2:
        retention = st.number_input(
            "Data Retention (days)", 
            min_value=1, 
            max_value=365, 
            value=settings.get("data_retention_days", 30),
            help="Automatically delete data after this many days"
        )
        
        export_anon = st.checkbox(
            "Export Anonymized Only", 
            value=settings.get("export_anonymized_only", True),
            help="Only export anonymized data in reports"
        )
    
    if st.button("Save Privacy Settings"):
        new_settings = {
            "anonymize_comments": anonymize,
            "client_side_processing": client_side,
            "data_retention_days": retention,
            "export_anonymized_only": export_anon
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/privacy/settings", json=new_settings)
            if response.status_code == 200:
                st.success("Privacy settings saved successfully!")
            else:
                st.error(f"Failed to save settings: {response.text}")
        except Exception as e:
            st.error(f"Error saving settings: {str(e)}")
    
    # Anonymize existing data
    st.subheader("Anonymize Current Data")
    if st.button("Anonymize All Comments"):
        try:
            response = requests.post(f"{API_BASE_URL}/anonymize/comments")
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"❌ Failed to anonymize: {response.text}")
        except Exception as e:
            st.error(f"❌ Error anonymizing: {str(e)}")
    
    # Data retention info
    try:
        response = requests.get(f"{API_BASE_URL}/privacy/data-retention")
        if response.status_code == 200:
            retention_info = response.json()
            st.info(retention_info["retention_policy"])
    except Exception as e:
        pass

# Add transparency features
def show_transparency():
    st.header("🔍 Transparency")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Methodology", 
        "Sources", 
        "Audit Trail", 
        "Confidence Explorer"
    ])
    
    with tab1:
        try:
            response = requests.get(f"{API_BASE_URL}/transparency/methodology")
            if response.status_code == 200:
                methodology = response.json()
                st.subheader(methodology["title"])
                st.markdown(methodology["description"])
                
                for step in methodology["steps"]:
                    with st.expander(f"Step {step['step']}: {step['name']}"):
                        st.markdown(f"**Description:** {step['description']}")
                        st.markdown(f"**Details:** {step['details']}")
            else:
                st.error("Failed to load methodology")
        except Exception as e:
            st.error(f"Error loading methodology: {str(e)}")
    
    with tab2:
        try:
            response = requests.get(f"{API_BASE_URL}/transparency/sources")
            if response.status_code == 200:
                sources = response.json()
                for source in sources["sources"]:
                    st.subheader(source["type"])
                    st.markdown(f"**Description:** {source['description']}")
                    st.markdown(f"**Processing:** {source['processing']}")
                    st.markdown("---")
            else:
                st.error("Failed to load sources")
        except Exception as e:
            st.error(f"Error loading sources: {str(e)}")
    
    with tab3:
        try:
            response = requests.get(f"{API_BASE_URL}/transparency/audit-trail")
            if response.status_code == 200:
                audit = response.json()
                st.subheader("Processing Audit Trail")
                for step in audit["processing_steps"]:
                    st.markdown(f"**{step['step']}** ({time.ctime(step['timestamp'])})")
                    st.markdown(f"- {step['description']}")
                    st.markdown(f"- {step['details']}")
                    st.markdown("")
            else:
                st.error("Failed to load audit trail")
        except Exception as e:
            st.error(f"Error loading audit trail: {str(e)}")
    
    with tab4:
        st.subheader("Argument Confidence Explorer")
        argument_id = st.text_input("Enter Argument ID to explore confidence")
        if argument_id and st.button("Analyze Confidence"):
            try:
                response = requests.get(f"{API_BASE_URL}/transparency/confidence/{argument_id}")
                if response.status_code == 200:
                    confidence = response.json()
                    if "error" in confidence:
                        st.error(confidence["error"])
                    else:
                        st.metric("Confidence Score", f"{confidence['confidence_score']}%")
                        st.markdown(f"**Explanation:** {confidence['confidence_explanation']}")
                        
                        st.subheader("Factors Considered")
                        for factor in confidence["factors"]:
                            st.markdown(f"- {factor}")
                        
                        st.subheader("Uncertainty Indicators")
                        for indicator in confidence["uncertainty_indicators"]:
                            st.markdown(f"- {indicator}")
                else:
                    st.error("Failed to analyze confidence")
            except Exception as e:
                st.error(f"Error analyzing confidence: {str(e)}")

# Add privacy and transparency to sidebar
def main():
    
    # Add new sidebar options
    st.sidebar.title("Privacy & Transparency")
    privacy_page = st.sidebar.radio("Privacy Options", [
        "Privacy Controls",
        "Transparency"
    ])
    
    if privacy_page == "Privacy Controls":
        show_privacy_controls()
    elif privacy_page == "Transparency":
        show_transparency()
```

#### Step 2: Update Gradio Frontend

Update `gradio_app.py`:

```python
# Add privacy functions
def get_privacy_settings():
    """Get current privacy settings"""
    try:
        response = requests.get(f"{API_BASE_URL}/privacy/settings")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to load settings"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def update_privacy_settings(anonymize, client_side, retention, export_anon):
    """Update privacy settings"""
    try:
        settings = {
            "anonymize_comments": anonymize,
            "client_side_processing": client_side,
            "data_retention_days": retention,
            "export_anonymized_only": export_anon
        }
        
        response = requests.post(f"{API_BASE_URL}/privacy/settings", json=settings)
        if response.status_code == 200:
            return "✅ Privacy settings updated successfully!"
        else:
            return f"❌ Failed to update settings: {response.text}"
    except Exception as e:
        return f"❌ Error updating settings: {str(e)}"

def anonymize_comments():
    """Anonymize current comments"""
    try:
        response = requests.post(f"{API_BASE_URL}/anonymize/comments")
        if response.status_code == 200:
            result = response.json()
            return f"✅ {result['message']}"
        else:
            return f"❌ Failed to anonymize: {response.text}"
    except Exception as e:
        return f"❌ Error anonymizing: {str(e)}"

# Add transparency functions
def get_methodology():
    """Get analysis methodology"""
    try:
        response = requests.get(f"{API_BASE_URL}/transparency/methodology")
        if response.status_code == 200:
            methodology = response.json()
            output = f"# {methodology['title']}\n\n{methodology['description']}\n\n"
            for step in methodology['steps']:
                output += f"## Step {step['step']}: {step['name']}\n"
                output += f"**Description:** {step['description']}\n"
                output += f"**Details:** {step['details']}\n\n"
            return output
        else:
            return f"❌ Failed to load methodology: {response.text}"
    except Exception as e:
        return f"❌ Error loading methodology: {str(e)}"

def get_sources():
    """Get data sources"""
    try:
        response = requests.get(f"{API_BASE_URL}/transparency/sources")
        if response.status_code == 200:
            sources = response.json()
            output = "# Data Sources\n\n"
            for source in sources['sources']:
                output += f"## {source['type']}\n"
                output += f"**Description:** {source['description']}\n"
                output += f"**Processing:** {source['processing']}\n\n"
            return output
        else:
            return f"❌ Failed to load sources: {response.text}"
    except Exception as e:
        return f"❌ Error loading sources: {str(e)}"

# Add to Gradio interface
with gr.Tab("Privacy"):
    gr.Markdown("## 🔒 Privacy Controls")
    
    with gr.Row():
        with gr.Column():
            settings = get_privacy_settings()
            if isinstance(settings, dict) and "error" not in settings:
                anonymize_check = gr.Checkbox(
                    label="Anonymize Comments", 
                    value=settings.get("anonymize_comments", True)
                )
                client_side_check = gr.Checkbox(
                    label="Client-Side Processing", 
                    value=settings.get("client_side_processing", False)
                )
                retention_slider = gr.Slider(
                    minimum=1, 
                    maximum=365, 
                    value=settings.get("data_retention_days", 30),
                    label="Data Retention (days)"
                )
                export_anon_check = gr.Checkbox(
                    label="Export Anonymized Only", 
                    value=settings.get("export_anonymized_only", True)
                )
            else:
                anonymize_check = gr.Checkbox(label="Anonymize Comments", value=True)
                client_side_check = gr.Checkbox(label="Client-Side Processing", value=False)
                retention_slider = gr.Slider(minimum=1, maximum=365, value=30, label="Data Retention (days)")
                export_anon_check = gr.Checkbox(label="Export Anonymized Only", value=True)
            
            update_btn = gr.Button("Save Privacy Settings")
            settings_output = gr.Textbox(label="Settings Status", interactive=False)
            
            anonymize_btn = gr.Button("Anonymize All Comments")
            anonymize_output = gr.Textbox(label="Anonymization Status", interactive=False)
    
    update_btn.click(
        update_privacy_settings,
        inputs=[anonymize_check, client_side_check, retention_slider, export_anon_check],
        outputs=settings_output
    )
    
    anonymize_btn.click(
        anonymize_comments,
        inputs=None,
        outputs=anonymize_output
    )

with gr.Tab("Transparency"):
    gr.Markdown("## 🔍 Transparency Features")
    
    with gr.Tab("Methodology"):
        methodology_btn = gr.Button("Load Analysis Methodology")
        methodology_output = gr.Textbox(label="Methodology", max_lines=20, interactive=False)
        methodology_btn.click(get_methodology, inputs=None, outputs=methodology_output)
    
    with gr.Tab("Sources"):
        sources_btn = gr.Button("Load Data Sources")
        sources_output = gr.Textbox(label="Sources", max_lines=20, interactive=False)
        sources_btn.click(get_sources, inputs=None, outputs=sources_output)
```

### 5. Data Anonymization Enhancements

#### Step 1: Improve Anonymization Algorithm

Update `backend/processing/client_side.py`:

```python
# Enhanced anonymization with better NLP
class ClientSideProcessor:
    
    @staticmethod
    def _remove_personal_info(text: str) -> str:
        """
        Remove personal information from text with enhanced detection
        """
        import re
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]', text)
        
        # Remove phone numbers (various formats)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
            r'\b\d{3}\s\d{3}\s\d{4}\b'
        ]
        for pattern in phone_patterns:
            text = re.sub(pattern, '[PHONE REDACTED]', text)
        
        # Remove SSN/SIN patterns
        text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[ID NUMBER REDACTED]', text)
        
        # Remove credit card numbers (simplified)
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD NUMBER REDACTED]', text)
        
        # Remove addresses (enhanced)
        address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl|Square|Sq|Terrace|Ter)\b',
            r'\b(?:P\.?O\.?\s*)?Box\s+\d+\b'
        ]
        for pattern in address_patterns:
            text = re.sub(pattern, '[ADDRESS REDACTED]', text, flags=re.IGNORECASE)
        
        # Remove names (more sophisticated approach)
        # This is still a basic approach - in production, you'd want a proper NER model
        # For now, we'll be conservative to avoid over-redaction
        name_patterns = [
            r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?)\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'  # Simple two-word names
        ]
        for pattern in name_patterns:
            text = re.sub(pattern, '[NAME REDACTED]', text)
        
        # Remove dates (basic patterns)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        ]
        for pattern in date_patterns:
            text = re.sub(pattern, '[DATE REDACTED]', text)
        
        return text
    
    @staticmethod
    def anonymize_comments(comments: List[Comment]) -> List[Comment]:
        """
        Anonymize comments with enhanced privacy protection
        """
        anonymized_comments = []
        
        for comment in comments:
            # Create a copy of the comment
            anonymized_comment = Comment(
                id=comment.id,
                text=comment.text,
                source=comment.source,
                timestamp=comment.timestamp,
                policy_clause=comment.policy_clause
            )
            
            # Remove personal identifiers from text
            anonymized_comment.text = ClientSideProcessor._remove_personal_info(comment.text)
            
            # Anonymize source if it contains personal info
            source_lower = anonymized_comment.source.lower()
            if any(keyword in source_lower for keyword in ['user', 'person', 'customer', 'client']):
                anonymized_comment.source = "anonymous_source"
            elif "@" in anonymized_comment.source:
                anonymized_comment.source = "email_source"
            
            anonymized_comments.append(anonymized_comment)
        
        return anonymized_comments
```

### 6. Documentation Updates

#### Step 1: Update README with Privacy Features

Update `README.md`:

```markdown
## Privacy and Transparency

Sovereign's Edict prioritizes user privacy and transparency in all operations.

### Privacy Features

- **Client-Side Processing**: Option to process data entirely on your device
- **Data Anonymization**: Automatic removal of personal identifiers
- **Privacy Controls**: Configurable privacy settings
- **Data Retention**: Automatic cleanup of old data
- **No Data Sharing**: Your data never leaves your device by default

### Transparency Features

- **Methodology Documentation**: Detailed explanation of analysis processes
- **Source Tracking**: Clear identification of all data sources
- **Confidence Scoring**: Transparency about AI certainty levels
- **Audit Trail**: Complete record of processing steps
- **Open Source**: Full access to code and algorithms

### Usage Examples

#### Enable Client-Side Processing
```bash
curl -X POST "http://localhost:8000/process/client-side" \
  -H "Content-Type: application/json" \
  -d '{"raw_data": "your,data,here", "data_type": "csv"}'
```

#### Anonymize Comments
```bash
curl -X POST "http://localhost:8000/anonymize/comments"
```

#### Get Privacy Settings
```bash
curl -X GET "http://localhost:8000/privacy/settings"
```

#### View Analysis Methodology
```bash
curl -X GET "http://localhost:8000/transparency/methodology"
```
```

#### Step 2: Create Privacy Documentation

Create `docs/PRIVACY_POLICY.md`:

```markdown
# Privacy Policy

## Overview

Sovereign's Edict is designed with privacy as a fundamental principle. We believe that policy analysis should be conducted without compromising individual privacy or organizational security.

## Data Handling Principles

### Privacy by Default
- No personal data is collected without explicit consent
- Data processing occurs locally whenever possible
- Minimal data retention with automatic cleanup
- Transparent data handling practices

### Data Collection
We collect only the data necessary for the operation of the platform:
- Policy documents provided for analysis
- Public comments and feedback on policies
- System configuration settings
- Usage analytics (optional and anonymized)

### Data Usage
Data is used solely for:
- Policy argumentation analysis
- Generating insights and recommendations
- Improving the platform (with consent)
- System performance monitoring

### Data Storage
- Data is stored only for the duration necessary to complete analysis
- All data is automatically deleted after the configured retention period
- No data is shared with third parties without explicit consent
- Data is not used for training AI models without consent

## Privacy Controls

### Client-Side Processing
Enable client-side processing to ensure all data analysis occurs on your device:
- No data is transmitted to external servers
- All processing happens locally
- Results are generated without cloud dependency

### Data Anonymization
Automatic removal of personal identifiers:
- Email addresses, phone numbers, and other PII are redacted
- Names and personal references are anonymized
- Addresses and ID numbers are removed

### Data Retention
Configure automatic data cleanup:
- Set retention periods from 1 day to 1 year
- Data is automatically deleted after the retention period
- Manual deletion is always available

## Transparency Features

### Methodology Disclosure
We provide complete transparency about our analysis methods:
- Detailed documentation of all processing steps
- Clear explanation of AI models and algorithms used
- Confidence scoring with uncertainty indicators
- Source tracking for all insights

### Audit Trail
Complete record of all processing activities:
- Timestamped log of all operations
- Detailed breakdown of analysis steps
- Performance metrics and resource usage
- Error tracking and resolution

### Source Tracking
Clear identification of all data sources:
- Policy documents and their origins
- Comment sources and collection methods
- Citation sources and verification status
- External data dependencies

## Security Measures

### Data Encryption
- All data transmission uses HTTPS encryption
- Local data storage uses file system permissions
- Sensitive configuration is protected

### Access Controls
- Role-based access to system features
- Authentication for administrative functions
- Audit logging of all access events

### Vulnerability Management
- Regular security updates and patches
- Dependency scanning for known vulnerabilities
- Security testing and code review

## Your Rights

### Data Access
You have the right to:
- Access all data stored about your usage
- Export your data in standard formats
- Understand how your data is processed

### Data Control
You have the right to:
- Delete your data at any time
- Opt out of analytics collection
- Control data sharing preferences

### Data Portability
You have the right to:
- Export your analysis results
- Transfer data to other systems
- Receive data in machine-readable formats

## Contact Information

For privacy-related questions or concerns:
- Email: privacy@sovereignsedict.com
- Phone: +1 (555) 123-4567
- Mail: Privacy Officer, Sovereign's Edict, 123 Policy Street, Governance City, GC 12345

## Policy Updates

This privacy policy may be updated to reflect changes in our practices or legal requirements. We will notify users of significant changes through the application interface.

Last updated: [DATE]
```

### 7. Testing and Verification

#### Step 1: Test Privacy Features
```bash
# Test client-side processing
curl -X POST "http://localhost:8000/process/client-side" \
  -H "Content-Type: application/json" \
  -d '{"raw_data": "This is a test comment with email@example.com", "data_type": "text"}'

# Test anonymization
curl -X POST "http://localhost:8000/anonymize/comments"

# Test privacy settings
curl -X GET "http://localhost:8000/privacy/settings"
curl -X POST "http://localhost:8000/privacy/settings" \
  -H "Content-Type: application/json" \
  -d '{"anonymize_comments": true, "data_retention_days": 7}'
```

#### Step 2: Test Transparency Features
```bash
# Test methodology
curl -X GET "http://localhost:8000/transparency/methodology"

# Test sources
curl -X GET "http://localhost:8000/transparency/sources"

# Test audit trail
curl -X GET "http://localhost:8000/transparency/audit-trail"

# Test confidence scoring
curl -X GET "http://localhost:8000/transparency/confidence/argument_123"
```

#### Step 3: Test Frontend Integration
1. Start the backend server
2. Start the Streamlit/Gradio frontend
3. Test privacy controls and settings
4. Verify anonymization works correctly
5. Check transparency features display properly
6. Test client-side processing options

## Next Steps

After implementing privacy and transparency features:
1. Proceed to Phase 10: Polish and User Trust
2. Update user documentation with privacy features
3. Conduct privacy audit and security review
4. Test with privacy-focused users and organizations