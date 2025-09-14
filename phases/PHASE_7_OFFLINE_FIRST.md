# Phase 7: Lightweight, Offline-First Implementation

## Overview
Implement quantized local models, bundle sample data, and optimize for offline use while maintaining functionality.

## Implementation Steps

### 1. Local Model Integration

#### Step 1: Integrate Llama.cpp for Local Inference

Create `backend/models/local_model.py`:

```python
"""
Local model integration for Sovereign's Edict using Llama.cpp
"""
import os
import json
import subprocess
import tempfile
from typing import List, Dict
from ..models.argument import Argument, ArgumentType
from ..models.comment import Comment

class LocalArgumentExtractor:
    def __init__(self, model_path: str = None):
        """
        Initialize local model extractor
        """
        self.model_path = model_path or os.getenv("LOCAL_MODEL_PATH", "models/llama-2-7b-chat.Q4_K_M.gguf")
        
        # Check if model exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Local model not found at {self.model_path}")
        
        # Llama.cpp executable path
        self.llama_cpp_path = os.getenv("LLAMA_CPP_PATH", "./llama.cpp/main")
        
        # Check if llama.cpp exists
        if not os.path.exists(self.llama_cpp_path):
            raise FileNotFoundError(f"Llama.cpp executable not found at {self.llama_cpp_path}")
    
    def extract_arguments(self, comments: List[Comment]) -> List[Argument]:
        """
        Extract arguments using local LLM
        """
        arguments = []
        
        # Process comments in batches to stay within context limits
        batch_size = 10
        for i in range(0, len(comments), batch_size):
            batch = comments[i:i+batch_size]
            batch_arguments = self._extract_batch_arguments(batch)
            arguments.extend(batch_arguments)
        
        return arguments
    
    def _extract_batch_arguments(self, comments: List[Comment]) -> List[Argument]:
        """
        Extract arguments from a batch of comments using local model
        """
        try:
            # Prepare the prompt
            prompt = self._create_extraction_prompt(comments)
            
            # Create temporary file for prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Create temporary file for output
            output_file = prompt_file + ".out"
            
            # Run llama.cpp
            cmd = [
                self.llama_cpp_path,
                "-m", self.model_path,
                "-f", prompt_file,
                "-n", "512",  # Max tokens to generate
                "-c", "2048",  # Context size
                "-b", "512",   # Batch size
                "-t", "4",     # Number of threads
                "--repeat_penalty", "1.2",
                "--temp", "0.7",
                "--top_k", "40",
                "--top_p", "0.95"
            ]
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up prompt file
            os.unlink(prompt_file)
            
            if result.returncode == 0:
                # Parse the output
                response_text = result.stdout
                arguments = self._parse_model_response(response_text, comments)
                return arguments
            else:
                raise Exception(f"Model inference failed: {result.stderr}")
                
        except Exception as e:
            print(f"Local model extraction failed: {str(e)}")
            # Fallback to basic extraction
            return self._fallback_extraction(comments)
    
    def _create_extraction_prompt(self, comments: List[Comment]) -> str:
        """
        Create prompt for local model
        """
        comment_texts = [f"{i+1}. {comment.text}" for i, comment in enumerate(comments)]
        comments_str = "\n".join(comment_texts)
        
        prompt = f"""
You are an expert policy analyst. Your task is to extract arguments from public comments on policy documents.

For each comment, identify:
1. The argument (a clear statement of support or objection)
2. The stance (support or objection)
3. The relevant clause/section
4. Any evidence, law, or example mentioned
5. A confidence score (0-100)

Format your response as a JSON array with objects containing:
{{"argument": "...", "stance": "support|objection", "clause": "...", "citation": "...", "confidence": 0-100}}

Comments to analyze:
{comments_str}

JSON Response:
"""
        
        return prompt
    
    def _parse_model_response(self, response_text: str, comments: List[Comment]) -> List[Argument]:
        """
        Parse model response
        """
        try:
            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                arguments = []
                for i, item in enumerate(parsed_data):
                    if isinstance(item, dict):
                        argument = Argument(
                            id=f"arg_{len(arguments)}",
                            text=item.get('argument', ''),
                            type=ArgumentType.SUPPORT if item.get('stance', '').lower() == 'support' else ArgumentType.OBJECTION,
                            clause=item.get('clause', 'unknown'),
                            themes=[item.get('theme', 'general')] if item.get('theme') else ['general'],
                            confidence=item.get('confidence', 50),
                            citations=[item.get('citation', '')] if item.get('citation') else [],
                            source_comment=comments[i % len(comments)].id if comments else None
                        )
                        arguments.append(argument)
                
                return arguments
            
        except Exception as e:
            print(f"Failed to parse model response: {str(e)}")
        
        # Fallback if parsing fails
        return self._fallback_extraction(comments)
    
    def _fallback_extraction(self, comments: List[Comment]) -> List[Argument]:
        """
        Fallback extraction method using basic NLP
        """
        arguments = []
        
        # Simple keyword-based extraction
        support_keywords = ['support', 'agree', 'favor', 'good', 'benefit', 'positive']
        objection_keywords = ['oppose', 'against', 'disagree', 'bad', 'harm', 'negative', 'concern']
        
        for comment in comments:
            text_lower = comment.text.lower()
            
            # Determine stance based on keywords
            support_count = sum(1 for kw in support_keywords if kw in text_lower)
            objection_count = sum(1 for kw in objection_keywords if kw in text_lower)
            
            if support_count > objection_count:
                stance = ArgumentType.SUPPORT
            elif objection_count > support_count:
                stance = ArgumentType.OBJECTION
            else:
                # Neutral or unclear - default to support for now
                stance = ArgumentType.SUPPORT
            
            # Create simple argument
            argument = Argument(
                id=f"arg_{len(arguments)}",
                text=comment.text[:200] + "..." if len(comment.text) > 200 else comment.text,
                type=stance,
                clause="general",
                themes=['general'],
                confidence=30,  # Low confidence for fallback
                citations=[],
                source_comment=comment.id
            )
            arguments.append(argument)
        
        return arguments

# Singleton instance
_local_extractor = None

def get_local_extractor():
    """
    Get singleton instance of local extractor
    """
    global _local_extractor
    if _local_extractor is None:
        try:
            _local_extractor = LocalArgumentExtractor()
        except Exception as e:
            print(f"Failed to initialize local extractor: {str(e)}")
            _local_extractor = None
    return _local_extractor
```

#### Step 2: Update Main API to Support Model Switching

Update `backend/main.py`:

```python
# Add import
from .models.local_model import get_local_extractor

# Add model selection endpoint
@app.post("/analyze/local")
async def analyze_comments_local():
    """
    Analyze uploaded comments using local model
    """
    if not stored_data["comments"]:
        raise HTTPException(status_code=400, detail="No comments uploaded")
    
    if not stored_data["policies"]:
        raise HTTPException(status_code=400, detail="No policy document uploaded")
    
    # Use local model
    local_extractor = get_local_extractor()
    if local_extractor is None:
        raise HTTPException(status_code=500, detail="Local model not available")
    
    try:
        arguments = local_extractor.extract_arguments(stored_data["comments"])
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
            "message": "Local analysis complete",
            "num_arguments": len(arguments),
            "clause_arguments": {clause: len(args) for clause, args in clause_arguments.items()},
            "suggestions": suggestions,
            "model": "local"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local analysis failed: {str(e)}")

# Update existing analyze endpoint to handle model selection
@app.post("/analyze")
async def analyze_comments(model: str = "gemini"):
    """
    Analyze uploaded comments and generate insights
    """
    if not stored_data["comments"]:
        raise HTTPException(status_code=400, detail="No comments uploaded")
    
    if not stored_data["policies"]:
        raise HTTPException(status_code=400, detail="No policy document uploaded")
    
    if model == "local":
        return await analyze_comments_local()
    
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
        "suggestions": suggestions,
        "model": "gemini"
    }
```

### 2. Sample Data Bundling

#### Step 1: Create Sample Data Directory

Create `data/sample/` directory structure:

```bash
mkdir -p data/sample/policies
mkdir -p data/sample/comments
mkdir -p data/sample/debates
```

#### Step 2: Add Sample Policy Documents

Create `data/sample/policies/digital_privacy_act.txt`:

```
DIGITAL PRIVACY PROTECTION ACT

Section 1. Purpose and Scope
This Act establishes comprehensive protections for personal data and digital privacy rights of all individuals within the jurisdiction.

Section 2. Definitions
(a) "Personal data" means any information relating to an identified or identifiable natural person.
(b) "Data controller" means the natural or legal person who determines the purposes and means of processing personal data.
(c) "Data processor" means a natural or legal person who processes personal data on behalf of the controller.

Section 3. Data Collection and Consent
(a) Data controllers must obtain explicit, informed consent before collecting personal data.
(b) Consent must be freely given, specific, informed, and unambiguous.
(c) Data subjects have the right to withdraw consent at any time.

Section 4. Data Subject Rights
(a) Right to access: Data subjects have the right to obtain confirmation and access to their personal data.
(b) Right to rectification: Data subjects have the right to correct inaccurate personal data.
(c) Right to erasure: Data subjects have the right to request deletion of their personal data.
(d) Right to data portability: Data subjects have the right to receive their data in a structured, machine-readable format.

Section 5. Data Security and Breach Notification
(a) Data controllers must implement appropriate technical and organizational measures to ensure data security.
(b) In case of a data breach, controllers must notify the supervisory authority within 72 hours.
(c) Controllers must also notify affected data subjects without undue delay if the breach is likely to result in a high risk to their rights and freedoms.

Section 6. International Data Transfers
(a) Personal data may only be transferred to countries that provide adequate levels of data protection.
(b) Standard contractual clauses or binding corporate rules may be used for transfers to countries without adequate protection.

Section 7. Enforcement and Penalties
(a) Violations of this Act may result in administrative fines of up to 4% of annual global turnover or €20 million, whichever is higher.
(b) The supervisory authority may also impose additional corrective measures.
```

#### Step 3: Add Sample Comments

Create `data/sample/comments/privacy_comments.csv`:

```csv
text,source,timestamp,policy_clause
"I strongly support this privacy act. We need stronger protections for personal data in the digital age.",forum,1623456789,Section 3
"The right to erasure is crucial for protecting individuals from data misuse. This should be a fundamental right.",blog,1623456790,Section 4
"I'm concerned about the penalties being too harsh on small businesses. There should be proportionality in enforcement.",news,1623456791,Section 7
"The data portability requirement will drive innovation and competition among service providers.",research,1623456792,Section 4
"International data transfers are essential for global business operations. The restrictions seem too broad.",corporate,1623456793,Section 6
"The 72-hour breach notification requirement is unrealistic for small organizations with limited resources.",tech_forum,1623456794,Section 5
"Explicit consent requirements will improve user trust and transparency in data collection practices.",privacy_advocate,1623456795,Section 3
"The definition of personal data needs to be more precise to avoid overreach in regulation.",legal_expert,1623456796,Section 2
"Data controllers should be required to conduct privacy impact assessments for high-risk processing activities.",policy_analyst,1623456797,Section 5
"The right to access personal data is fundamental to individual autonomy and should be easily exercisable.",civil_rights_group,1623456798,Section 4
```

#### Step 4: Add Sample Debate Transcript

Create `data/sample/debates/privacy_hearing.txt`:

```
TRANSCRIPT OF PUBLIC HEARING ON DIGITAL PRIVACY PROTECTION ACT

CHAIRPERSON: Good morning. We're here today to discuss the proposed Digital Privacy Protection Act. I'd like to welcome our witnesses and thank everyone for attending.

DR. SARAH CHEN, PRIVACY ADVOCATE: Thank you for the opportunity to speak. I strongly support this legislation. The current patchwork of privacy laws is inadequate. We need comprehensive federal protections.

MR. JAMES WRIGHT, SMALL BUSINESS OWNER: While I understand the need for privacy protections, I'm concerned about the compliance burden on small businesses. The administrative costs could be devastating for companies like mine.

PROF. MARIA RODRIGUEZ, LEGAL SCHOLAR: The Act's approach to data subject rights is well-balanced. The right to erasure and data portability provisions are particularly important in today's digital economy.

MS. ROBERT JOHNSON, TECHNOLOGY EXECUTIVE: The international data transfer restrictions will harm American competitiveness. We need to ensure our companies can operate globally while maintaining appropriate protections.

DR. LISA KIM, CYBERSECURITY EXPERT: The security requirements are essential but need to be technology-neutral and risk-based. One-size-fits-all approaches rarely work in cybersecurity.

CHAIRPERSON: Thank you all for your testimony. We'll now open the floor for public comments.

AUDIENCE MEMBER 1: As a consumer, I want strong privacy protections. The right to access and correct my data should be guaranteed.

AUDIENCE MEMBER 2: I run a small online store with three employees. The proposed fines could put me out of business. There needs to be a small business exemption.

AUDIENCE MEMBER 3: The breach notification requirements are crucial for public safety. People deserve to know when their data has been compromised.

AUDIENCE MEMBER 4: I'm a software developer. The data portability requirements will encourage innovation and give users more control over their information.

CHAIRPERSON: Thank you for your comments. This concludes today's hearing. The committee will review all testimony and comments before finalizing the legislation.
```

#### Step 5: Create Sample Data Loader

Create `backend/utils/sample_data.py`:

```python
"""
Sample data loader for Sovereign's Edict
"""
import os
import csv
import json
from typing import List
from ..models.comment import Comment
from ..models.policy import PolicyDocument, PolicyClause
import uuid

def load_sample_policy() -> PolicyDocument:
    """
    Load sample policy document
    """
    policy_path = "data/sample/policies/digital_privacy_act.txt"
    
    if not os.path.exists(policy_path):
        raise FileNotFoundError(f"Sample policy not found at {policy_path}")
    
    with open(policy_path, 'r') as f:
        content = f.read()
    
    # Create clauses from sections
    clauses = []
    sections = content.split('\n\n')
    for i, section in enumerate(sections):
        if section.strip():
            clause = PolicyClause(
                id=f"clause_{i+1}",
                text=section.strip(),
                section=f"Section {i+1}"
            )
            clauses.append(clause)
    
    policy = PolicyDocument(
        id="sample_policy_001",
        title="Digital Privacy Protection Act",
        content=content,
        clauses=clauses
    )
    
    return policy

def load_sample_comments() -> List[Comment]:
    """
    Load sample comments
    """
    comments_path = "data/sample/comments/privacy_comments.csv"
    
    if not os.path.exists(comments_path):
        raise FileNotFoundError(f"Sample comments not found at {comments_path}")
    
    comments = []
    with open(comments_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            comment = Comment(
                id=str(uuid.uuid4()),
                text=row['text'],
                source=row['source'],
                timestamp=int(row['timestamp']) if row['timestamp'] else len(comments),
                policy_clause=row['policy_clause']
            )
            comments.append(comment)
    
    return comments

def load_sample_debate() -> List[Comment]:
    """
    Load sample debate transcript as comments
    """
    debate_path = "data/sample/debates/privacy_hearing.txt"
    
    if not os.path.exists(debate_path):
        raise FileNotFoundError(f"Sample debate not found at {debate_path}")
    
    with open(debate_path, 'r') as f:
        content = f.read()
    
    # Split into individual statements
    statements = content.split('\n\n')
    comments = []
    
    for i, statement in enumerate(statements):
        if statement.strip() and ':' in statement:
            # Extract speaker and statement
            parts = statement.split(':', 1)
            if len(parts) == 2:
                speaker, text = parts
                comment = Comment(
                    id=str(uuid.uuid4()),
                    text=text.strip(),
                    source=f"hearing_speaker_{speaker.strip()}",
                    timestamp=i,
                    policy_clause="debate_transcript"
                )
                comments.append(comment)
    
    return comments

def load_all_sample_data():
    """
    Load all sample data
    """
    try:
        policy = load_sample_policy()
        comments = load_sample_comments()
        debate_comments = load_sample_debate()
        
        # Combine all comments
        all_comments = comments + debate_comments
        
        return {
            "policy": policy,
            "comments": all_comments
        }
    except Exception as e:
        print(f"Failed to load sample data: {str(e)}")
        return None
```

#### Step 6: Add Sample Data Endpoint

Update `backend/main.py`:

```python
# Add import
from .utils.sample_data import load_all_sample_data

# Add endpoint for loading sample data
@app.post("/load/sample")
async def load_sample_data():
    """
    Load sample policy and comments for demonstration
    """
    try:
        sample_data = load_all_sample_data()
        
        if sample_data is None:
            raise HTTPException(status_code=500, detail="Failed to load sample data")
        
        # Store in memory
        stored_data["policies"] = [sample_data["policy"]]
        stored_data["comments"] = sample_data["comments"]
        
        return {
            "message": "Sample data loaded successfully",
            "policy_title": sample_data["policy"].title,
            "num_comments": len(sample_data["comments"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample data: {str(e)}")
```

### 3. Offline Mode Implementation

#### Step 1: Create Offline Mode Configuration

Create `backend/config/offline_config.py`:

```python
"""
Offline mode configuration for Sovereign's Edict
"""
import os
from typing import Dict, Any

class OfflineConfig:
    def __init__(self):
        self.offline_mode = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        self.local_model_path = os.getenv("LOCAL_MODEL_PATH", "models/llama-2-7b-chat.Q4_K_M.gguf")
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_dir = os.getenv("CACHE_DIR", "data/cache")
        self.sample_data_enabled = os.getenv("SAMPLE_DATA_ENABLED", "true").lower() == "true"
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "offline_mode": self.offline_mode,
            "local_model_path": self.local_model_path,
            "cache_enabled": self.cache_enabled,
            "cache_dir": self.cache_dir,
            "sample_data_enabled": self.sample_data_enabled
        }

# Global configuration instance
config = OfflineConfig()
```

#### Step 2: Update Main Application for Offline Mode

Update `backend/main.py`:

```python
# Add import
from .config.offline_config import config

# Update app initialization
app = FastAPI(
    title="Sovereign's Edict",
    description="An Actionable Intelligence Platform for Clause-Level Policy Argumentation",
    version="0.1.0",
    docs_url="/docs" if not config.offline_mode else None,
    redoc_url="/redoc" if not config.offline_mode else None
)

# Add offline mode endpoint
@app.get("/config")
async def get_config():
    """
    Get current configuration
    """
    return config.to_dict()

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    status = {
        "status": "healthy",
        "offline_mode": config.offline_mode,
        "local_model_available": get_local_extractor() is not None if config.offline_mode else None,
        "sample_data_enabled": config.sample_data_enabled
    }
    return status
```

### 4. Frontend Updates for Offline Mode

#### Step 1: Update Streamlit Frontend

Update `streamlit_app.py`:

```python
# Add offline mode detection
def is_offline_mode():
    try:
        response = requests.get(f"{API_BASE_URL}/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            return config.get("offline_mode", False)
    except:
        pass
    return False

# Update main function to show offline mode status
def main():
    st.title("🏛️ Sovereign's Edict")
    
    # Show offline mode status
    offline_mode = is_offline_mode()
    if offline_mode:
        st.info("🔒 Running in offline mode with local AI model")
    else:
        st.info("☁️ Running in online mode with cloud AI services")
    
    # ... rest of existing code ...

# Add sample data loading option
def show_upload():
    st.header("📤 Upload Data")
    
    # Add sample data option
    if st.checkbox("Load Sample Data for Demo"):
        if st.button("Load Sample Data"):
            try:
                response = requests.post(f"{API_BASE_URL}/load/sample")
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result['message']}")
                    st.session_state.data_uploaded = True
                else:
                    st.error(f"❌ Failed to load sample data: {response.text}")
            except Exception as e:
                st.error(f"❌ Error loading sample data: {str(e)}")
    
    # ... rest of existing upload code ...

# Update analyze function to support model selection
def show_analyze():
    st.header("🔍 Analyze Data")
    
    if not st.session_state.data_uploaded:
        st.warning("Please upload data first in the Upload Data section.")
        return
    
    # Model selection
    offline_mode = is_offline_mode()
    if offline_mode:
        model_option = "local"
        st.info("Using local AI model for analysis")
    else:
        model_option = st.radio("Select Analysis Model", ["gemini", "local"])
    
    # Analysis options
    st.subheader("Analysis Options")
    quick_mode = st.checkbox("Quick Demo Mode (First 50 comments)", value=True)
    st.markdown("*Quick mode is recommended for faster results during testing*")
    
    if st.button("🚀 Run Analysis"):
        try:
            with st.spinner("Analyzing data... This may take a few minutes."):
                params = {}
                if quick_mode:
                    params["limit"] = 50
                
                if model_option == "local" or offline_mode:
                    response = requests.post(f"{API_BASE_URL}/analyze/local", params=params)
                else:
                    response = requests.post(f"{API_BASE_URL}/analyze?model=gemini", params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis completed successfully!")
                    st.session_state.analysis_complete = True
                    
                    # Display summary
                    st.subheader("Analysis Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Arguments Extracted", result.get("num_arguments", 0))
                    with col2:
                        st.metric("Clauses Analyzed", len(result.get("clause_arguments", {})))
                    with col3:
                        st.metric("Suggestions Generated", len(result.get("suggestions", [])))
                    
                    # Store dashboard data
                    dashboard_response = requests.get(f"{API_BASE_URL}/results/dashboard")
                    if dashboard_response.status_code == 200:
                        st.session_state.dashboard_data = dashboard_response.json()
                else:
                    st.error(f"Analysis failed: {response.text}")
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
```

#### Step 2: Update Gradio Frontend

Update `gradio_app.py`:

```python
# Add model selection to analyze function
def run_analysis(quick_mode, model_option):
    """Run policy analysis"""
    try:
        params = {}
        if quick_mode:
            params["limit"] = 50
        
        if model_option == "local":
            response = requests.post(f"{API_BASE_URL}/analyze/local", params=params)
        else:
            response = requests.post(f"{API_BASE_URL}/analyze?model=gemini", params=params)
        
        if response.status_code == 200:
            result = response.json()
            summary = f"""
            ✅ Analysis completed successfully!
            
            **Summary:**
            - Arguments Extracted: {result.get('num_arguments', 0)}
            - Clauses Analyzed: {len(result.get('clause_arguments', {}))}
            - Suggestions Generated: {len(result.get('suggestions', []))}
            - Model Used: {result.get('model', 'unknown')}
            """
            return summary
        else:
            return f"❌ Analysis failed: {response.text}"
    except Exception as e:
        return f"❌ Error during analysis: {str(e)}"

# Update analyze tab
with gr.Tab("Analyze"):
    gr.Markdown("## Step 3: Run Analysis")
    with gr.Row():
        with gr.Column():
            quick_mode = gr.Checkbox(label="Quick Demo Mode (First 50 comments)", value=True)
            model_option = gr.Radio(label="Analysis Model", choices=["gemini", "local"], value="gemini")
            analyze_btn = gr.Button("🚀 Run Analysis")
            analysis_output = gr.Textbox(label="Analysis Status", interactive=False)
    
    analyze_btn.click(run_analysis, inputs=[quick_mode, model_option], outputs=analysis_output)

# Add sample data loading
def load_sample_data():
    """Load sample data"""
    try:
        response = requests.post(f"{API_BASE_URL}/load/sample")
        if response.status_code == 200:
            result = response.json()
            return f"✅ {result['message']}"
        else:
            return f"❌ Failed to load sample data: {response.text}"
    except Exception as e:
        return f"❌ Error loading sample data: {str(e)}"

# Add to Upload Data tab
with gr.Tab("Upload Data"):
    # ... existing upload code ...
    
    gr.Markdown("## Or Load Sample Data")
    sample_btn = gr.Button("Load Sample Data for Demo")
    sample_output = gr.Textbox(label="Sample Data Status", interactive=False)
    
    sample_btn.click(load_sample_data, inputs=None, outputs=sample_output)
```

### 5. Documentation and Installation Updates

#### Step 1: Update README with Offline Instructions

Update `README.md`:

```markdown
## Lightweight, Offline-First Mode

Sovereign's Edict can run completely offline with local AI models for privacy and portability.

### Offline Mode Features

- **Local AI Processing**: Uses quantized LLMs for argument extraction
- **No Internet Required**: All processing happens on your machine
- **Privacy First**: No data leaves your computer
- **Sample Data Included**: Pre-loaded policies and comments for immediate testing

### Setting Up Offline Mode

1. Download a quantized LLM model (e.g., Llama-2-7B in GGUF format)
2. Place the model in the `models/` directory
3. Set environment variables:
   ```bash
   export OFFLINE_MODE=true
   export LOCAL_MODEL_PATH=models/llama-2-7b-chat.Q4_K_M.gguf
   ```

### Running in Offline Mode

```bash
# Start backend in offline mode
OFFLINE_MODE=true python backend/main.py

# Load sample data and run analysis
curl -X POST "http://localhost:8000/load/sample"
curl -X POST "http://localhost:8000/analyze/local"
```

### Benefits of Offline Mode

- **Complete Privacy**: No data transmission to external services
- **No API Costs**: Eliminates cloud API usage fees
- **Always Available**: Works without internet connectivity
- **Fast Iteration**: Local processing for quick experimentation
```

#### Step 2: Create Offline Setup Guide

Create `docs/OFFLINE_MODE.md`:

```markdown
# Offline Mode Setup Guide

## Overview

Sovereign's Edict can operate completely offline using local AI models, ensuring maximum privacy and eliminating dependency on cloud services.

## Prerequisites

- Python 3.8+
- 8GB+ RAM (16GB recommended)
- 10GB+ free disk space for model files

## Setting Up Local Models

### Option 1: Download Pre-Quantized Models

1. Visit the [Llama.cpp models repository](https://huggingface.co/TheBloke)
2. Download a quantized model (e.g., `llama-2-7b-chat.Q4_K_M.gguf`)
3. Place the model file in the `models/` directory

### Option 2: Convert Your Own Models

1. Clone Llama.cpp:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   ```

2. Follow the [conversion guide](https://github.com/ggerganov/llama.cpp#description) to convert models

## Configuration

Set these environment variables to enable offline mode:

```bash
export OFFLINE_MODE=true
export LOCAL_MODEL_PATH=models/llama-2-7b-chat.Q4_K_M.gguf
export CACHE_ENABLED=true
export CACHE_DIR=data/cache
```

## Running Offline

### With Docker

```bash
docker-compose -f docker-compose.offline.yml up
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
OFFLINE_MODE=true python backend/main.py

# Start frontend
streamlit run streamlit_app.py
```

## Performance Considerations

- **Processing Time**: Local inference is slower than cloud APIs
- **Memory Usage**: Models require significant RAM
- **Accuracy**: May be lower than advanced cloud models
- **Batch Size**: Process smaller batches for better performance

## Troubleshooting

### Model Not Found
Ensure the model file exists at the specified path and has correct permissions.

### Memory Issues
Reduce batch size or use more quantized models (Q2_K, Q3_K, etc.).

### Slow Performance
Use fewer threads or reduce context size in the local model configuration.
```

### 6. Testing and Verification

#### Step 1: Test Local Model Integration
```bash
# Download a small test model
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -O models/tinyllama.gguf

# Set environment variables
export OFFLINE_MODE=true
export LOCAL_MODEL_PATH=models/tinyllama.gguf

# Start backend
python backend/main.py
```

#### Step 2: Test Sample Data Loading
```bash
# Load sample data
curl -X POST "http://localhost:8000/load/sample"

# Run local analysis
curl -X POST "http://localhost:8000/analyze/local"
```

#### Step 3: Test Frontend Integration
1. Start the backend with offline mode enabled
2. Start the Streamlit frontend
3. Verify sample data loading works
4. Test local model analysis
5. Check that UI properly indicates offline mode

### 7. Performance Optimization

#### For Local Models:
1. Implement model quantization for smaller file sizes
2. Add progress indicators for long-running local inference
3. Optimize batch sizes based on available system resources
4. Implement caching for repeated analyses

## Next Steps

After implementing lightweight, offline-first features:
1. Proceed to Phase 8: Community/Operator Mode
2. Update user documentation with offline mode instructions
3. Test performance on different hardware configurations
4. Optimize local model integration for better accuracy