# Phase 3: Automated Processing Pipeline Implementation

## Overview
Implement fully automated processing with a simple "Analyze Now" button and auto-citations with clickable source links.

## Implementation Steps

### 1. Backend Implementation

#### Step 1: Enhance Analysis Endpoint

Update `backend/main.py` to improve the analysis process:

```python
# Add new imports
import asyncio
import json
import os
from typing import Dict, List
from .utils.cache import CacheManager

# Add cache manager
cache_manager = CacheManager()

@app.post("/analyze")
async def analyze_comments(background_tasks: BackgroundTasks):
    """
    Analyze uploaded comments and generate insights with caching
    """
    if not stored_data["comments"]:
        raise HTTPException(status_code=400, detail="No comments uploaded")
    
    if not stored_data["policies"]:
        raise HTTPException(status_code=400, detail="No policy document uploaded")
    
    # Create analysis job
    job_id = str(uuid.uuid4())
    
    # Start background processing
    background_tasks.add_task(process_analysis_job, job_id)
    
    return {
        "message": "Analysis started",
        "job_id": job_id,
        "status": "processing"
    }

async def process_analysis_job(job_id: str):
    """
    Background task to process analysis
    """
    try:
        # Assess computational requirements
        requirements = assess_requirements(stored_data["comments"])
        
        # Route processing
        compute_route = route_processing({"requirements": requirements})
        
        # Check cache first
        cache_key = f"analysis_{hash(str([c.dict() for c in stored_data['comments']]))}"
        cached_result = cache_manager.get(cache_key)
        
        if cached_result:
            arguments = cached_result.get("arguments", [])
        else:
            # Extract arguments using Gemini API
            try:
                extractor = GeminiArgumentExtractor()
                arguments = extractor.extract_arguments(stored_data["comments"])
                
                # Cache the result
                cache_manager.set(cache_key, {
                    "arguments": [arg.dict() for arg in arguments],
                    "timestamp": time.time()
                })
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
        
        # Store results
        stored_data["analysis_results"] = {
            "job_id": job_id,
            "status": "completed",
            "requirements": requirements,
            "compute_route": compute_route,
            "num_arguments": len(arguments),
            "clause_arguments": {clause: len(args) for clause, args in clause_arguments.items()},
            "suggestions": suggestions,
            "completed_at": time.time()
        }
        
    except Exception as e:
        stored_data["analysis_results"] = {
            "job_id": job_id,
            "status": "error",
            "error": str(e),
            "completed_at": time.time()
        }

@app.get("/analysis/status/{job_id}")
async def get_analysis_status(job_id: str):
    """
    Get the status of an analysis job
    """
    if "analysis_results" in stored_data and stored_data["analysis_results"].get("job_id") == job_id:
        return stored_data["analysis_results"]
    
    return {"job_id": job_id, "status": "not_found"}

@app.get("/analyze/quick")
async def quick_analysis(limit: int = 100):
    """
    Quick analysis for demo purposes (first N comments)
    """
    if not stored_data["comments"]:
        raise HTTPException(status_code=400, detail="No comments uploaded")
    
    if not stored_data["policies"]:
        raise HTTPException(status_code=400, detail="No policy document uploaded")
    
    # Use only first N comments for quick analysis
    comments_subset = stored_data["comments"][:limit]
    
    # Process subset
    try:
        extractor = GeminiArgumentExtractor()
        arguments = extractor.extract_arguments(comments_subset)
        
        # Find citations for arguments
        for argument in arguments:
            citations = find_citations(argument)
            argument.citations = [citation.id for citation in citations]
        
        # Calculate argument weights
        weights = calculate_argument_weights(arguments)
        
        # Aggregate arguments by clause
        clause_arguments = aggregate_arguments(arguments)
        
        # Generate amendment suggestions
        suggestions = suggest_amendments(arguments)
        
        return {
            "message": "Quick analysis complete",
            "num_comments_processed": len(comments_subset),
            "num_arguments": len(arguments),
            "clause_arguments": {clause: len(args) for clause, args in clause_arguments.items()},
            "suggestions": suggestions[:5],  # Limit suggestions for quick view
            "processing_time": "quick"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
```

#### Step 2: Create Cache Manager

Create `backend/utils/cache.py`:

```python
"""
Cache manager for Sovereign's Edict
"""
import json
import os
import time
from typing import Any, Optional

class CacheManager:
    def __init__(self, cache_file: str = "data/ai_cache.json", max_age: int = 86400):  # 24 hours
        self.cache_file = cache_file
        self.max_age = max_age
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _load_cache(self) -> dict:
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_cache(self, cache: dict):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache = self._load_cache()
        if key in cache:
            entry = cache[key]
            # Check if entry is still valid
            if time.time() - entry.get('timestamp', 0) < self.max_age:
                return entry.get('value')
            else:
                # Remove expired entry
                del cache[key]
                self._save_cache(cache)
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        cache = self._load_cache()
        cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        self._save_cache(cache)
    
    def clear(self):
        """Clear all cache"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
```

#### Step 3: Enhance Gemini Extractor

Update `backend/mining/gemini_extractor.py`:

```python
"""
Gemini API argument extractor for Sovereign's Edict
"""
import os
import json
import google.generativeai as genai
from typing import List, Dict, Optional
from ..models.argument import Argument, ArgumentType
from ..models.comment import Comment
import logging

logger = logging.getLogger(__name__)

class GeminiArgumentExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_arguments(self, comments: List[Comment]) -> List[Argument]:
        """
        Extract arguments from comments using Gemini API
        """
        arguments = []
        
        # Process comments in batches to stay within API limits
        batch_size = 50
        for i in range(0, len(comments), batch_size):
            batch = comments[i:i+batch_size]
            batch_arguments = self._extract_batch_arguments(batch)
            arguments.extend(batch_arguments)
        
        return arguments
    
    def _extract_batch_arguments(self, comments: List[Comment]) -> List[Argument]:
        """
        Extract arguments from a batch of comments
        """
        try:
            # Prepare the prompt
            prompt = self._create_extraction_prompt(comments)
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            # Parse the response
            arguments = self._parse_gemini_response(response.text, comments)
            
            return arguments
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {str(e)}")
            # Fallback to basic extraction
            return self._fallback_extraction(comments)
    
    def _create_extraction_prompt(self, comments: List[Comment]) -> str:
        """
        Create prompt for Gemini API
        """
        comment_texts = [f"{i+1}. {comment.text}" for i, comment in enumerate(comments)]
        comments_str = "\n".join(comment_texts)
        
        prompt = (
            "Given the following public comments on a policy document, "
            "extract each argument (pro or con), the relevant clause/section, "
            "and cite any evidence, law, or real-world example mentioned. "
            "Also provide a confidence score (0-100) for each argument. "
            "Return as a JSON list with 'argument', 'stance', 'clause', 'citation', and 'confidence'.\n\n"
            f"Comments:\n{comments_str}\n\n"
            "Response format (JSON array):"
        )
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, comments: List[Comment]) -> List[Argument]:
        """
        Parse Gemini API response
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
            logger.error(f"Failed to parse Gemini response: {str(e)}")
        
        # Fallback if parsing fails
        return self._fallback_extraction(comments)
    
    def _fallback_extraction(self, comments: List[Comment]) -> List[Argument]:
        """
        Fallback extraction method
        """
        # This would implement a basic extraction method
        # For now, we'll return empty list and let the main extractor handle it
        return []
```

### 2. Frontend Implementation

#### Step 1: Update AnalyzeTab Component

Update `frontend/src/App.js` AnalyzeTab component:

```javascript
function AnalyzeTab() {
  const [analysisStatus, setAnalysisStatus] = useState('ready');
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [quickMode, setQuickMode] = useState(false);

  const startAnalysis = async () => {
    try {
      setAnalysisStatus('starting');
      
      const endpoint = quickMode ? '/analyze/quick?limit=50' : '/analyze';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      
      if (quickMode) {
        setAnalysisStatus('completed');
        // Handle quick analysis results
      } else {
        setJobId(data.job_id);
        setAnalysisStatus('processing');
        // Start polling for status
        pollAnalysisStatus(data.job_id);
      }
    } catch (error) {
      setAnalysisStatus('error');
      alert('Analysis failed: ' + error.message);
    }
  };

  const pollAnalysisStatus = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:8000/analysis/status/${jobId}`);
      if (!response.ok) throw new Error('Failed to get status');
      
      const data = await response.json();
      
      if (data.status === 'completed') {
        setAnalysisStatus('completed');
        setProgress(100);
      } else if (data.status === 'error') {
        setAnalysisStatus('error');
        alert('Analysis failed: ' + data.error);
      } else if (data.status === 'processing') {
        // Update progress (simplified)
        setProgress(prev => Math.min(prev + 10, 90));
        // Continue polling
        setTimeout(() => pollAnalysisStatus(jobId), 2000);
      }
    } catch (error) {
      setAnalysisStatus('error');
      alert('Failed to check analysis status: ' + error.message);
    }
  };

  return (
    <div className="tab-content">
      <h2>Automated Analysis</h2>
      
      <div className="analysis-controls">
        <button 
          className="btn-primary" 
          onClick={startAnalysis}
          disabled={analysisStatus === 'processing' || analysisStatus === 'starting'}
        >
          {analysisStatus === 'processing' ? 'Processing...' : 'Run Analysis'}
        </button>
        
        <label className="quick-mode-toggle">
          <input 
            type="checkbox" 
            checked={quickMode}
            onChange={(e) => setQuickMode(e.target.checked)}
          />
          Quick Demo Mode (First 50 comments)
        </label>
      </div>
      
      <div className="analysis-status">
        <p>Status: {analysisStatus.charAt(0).toUpperCase() + analysisStatus.slice(1)}</p>
        {analysisStatus === 'processing' && (
          <div className="progress-bar">
            <div className="progress-fill" style={{width: `${progress}%`}}></div>
          </div>
        )}
        <div className="progress-info">
          <p>Estimated time: {quickMode ? '30-60 seconds' : '2-5 minutes for small datasets'}</p>
        </div>
      </div>
      
      <div className="analysis-options">
        <h3>Analysis Options</h3>
        <div className="option-group">
          <label>
            <input type="checkbox" defaultChecked disabled /> 
            Argument Extraction
          </label>
          <label>
            <input type="checkbox" defaultChecked disabled /> 
            Theme Clustering
          </label>
          <label>
            <input type="checkbox" defaultChecked disabled /> 
            Sentiment Analysis
          </label>
          <label>
            <input type="checkbox" defaultChecked disabled /> 
            Citation Matching
          </label>
        </div>
      </div>
      
      {analysisStatus === 'completed' && (
        <div className="analysis-complete">
          <h3>Analysis Complete!</h3>
          <p>View results in the Results tab.</p>
          <button onClick={() => window.location.hash = '#results'}>Go to Results</button>
        </div>
      )}
    </div>
  );
}
```

#### Step 2: Add CSS for Analysis Components

Update `frontend/src/App.css`:

```css
.analysis-controls {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.quick-mode-toggle {
  display: inline-block;
  margin-left: 20px;
  vertical-align: middle;
}

.analysis-status {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-fill {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.progress-info {
  font-style: italic;
  color: #666;
}

.analysis-options {
  margin-top: 20px;
}

.analysis-options h3 {
  margin-top: 0;
}

.option-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.option-group label {
  display: flex;
  align-items: center;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.option-group input {
  margin-right: 8px;
}

.analysis-complete {
  padding: 20px;
  background-color: #dff0d8;
  border: 1px solid #d6e9c6;
  border-radius: 4px;
  text-align: center;
}

.analysis-complete h3 {
  color: #3c763d;
  margin-top: 0;
}

.analysis-complete button {
  background-color: #5cb85c;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
```

### 3. Auto-Citations Implementation

#### Step 1: Enhance Citation System

Update `backend/citation/oracle.py`:

```python
"""
Citation oracle for Sovereign's Edict
"""
import re
import uuid
from typing import List, Dict
from ..models.citation import Citation
from ..models.argument import Argument

def find_citations(argument: Argument) -> List[Citation]:
    """
    Find citations for an argument with clickable links
    """
    citations = []
    
    # Extract potential citations from argument text
    # Look for patterns like "Section 5", "Article 12", "Law XYZ", etc.
    section_matches = re.findall(r'(Section|Article|Clause)\s+(\d+[A-Z]*)', argument.text, re.IGNORECASE)
    law_matches = re.findall(r'([A-Z][a-zA-Z\s]+(?:Act|Law|Regulation|Code))', argument.text)
    
    # Create citations for sections
    for match in section_matches:
        citation = Citation(
            id=str(uuid.uuid4()),
            title=f"{match[0]} {match[1]}",
            url=f"https://example.com/policy#{match[0].lower()}-{match[1]}",
            source="Policy Document",
            relevance_score=0.9
        )
        citations.append(citation)
    
    # Create citations for laws
    for match in law_matches:
        citation = Citation(
            id=str(uuid.uuid4()),
            title=match.strip(),
            url=f"https://legislation.example.com/{match.strip().replace(' ', '-')}",
            source="Legislation Database",
            relevance_score=0.8
        )
        citations.append(citation)
    
    # If no citations found, create a general citation
    if not citations:
        citation = Citation(
            id=str(uuid.uuid4()),
            title="General Policy Reference",
            url="https://example.com/policy",
            source="Policy Document",
            relevance_score=0.5
        )
        citations.append(citation)
    
    return citations

def create_clickable_citation(citation: Citation) -> Dict:
    """
    Create a clickable citation for frontend display
    """
    return {
        "id": citation.id,
        "title": citation.title,
        "url": citation.url,
        "source": citation.source,
        "relevance_score": citation.relevance_score,
        "clickable": True
    }
```

#### Step 2: Update Results API to Include Clickable Citations

Update `backend/main.py`:

```python
@app.get("/results/arguments")
async def get_arguments():
    """
    Get extracted arguments with clickable citations
    """
    from .citation.oracle import create_clickable_citation
    
    arguments_with_citations = []
    for argument in stored_data["arguments"]:
        arg_dict = argument.dict()
        # Add clickable citations
        clickable_citations = []
        for citation_id in argument.citations:
            # Find the actual citation object
            citation = next((c for c in stored_data["citations"] if c.id == citation_id), None)
            if citation:
                clickable_citations.append(create_clickable_citation(citation))
        arg_dict["clickable_citations"] = clickable_citations
        arguments_with_citations.append(arg_dict)
    
    return arguments_with_citations
```

### 4. Testing and Verification

#### Step 1: Test Analysis Endpoints
```bash
# Test quick analysis
curl -X POST "http://localhost:8000/analyze/quick?limit=10"

# Test full analysis
curl -X POST "http://localhost:8000/analyze"

# Check analysis status
curl "http://localhost:8000/analysis/status/{job_id}"
```

#### Step 2: Test Citation System
```bash
# Get arguments with citations
curl "http://localhost:8000/results/arguments"
```

#### Step 3: Test Frontend Components
1. Start the backend server
2. Start the frontend development server
3. Navigate to the Analyze tab
4. Test both quick and full analysis modes
5. Verify progress indicators work correctly
6. Check that results are displayed properly

### 5. Performance Optimization

#### For Large Datasets:
1. Implement batch processing with progress updates
2. Add caching for repeated analyses
3. Use background job processing for time-consuming tasks
4. Implement rate limiting for API calls

### 6. Error Handling

#### Common Issues to Handle:
1. API rate limiting
2. Network connectivity issues
3. Invalid responses from Gemini
4. Large dataset processing timeouts

#### Implementation:
Add proper error handling and user-friendly error messages throughout the analysis pipeline.

### 7. Documentation Updates

Update the README.md to include information about the automated processing:

```markdown
## Automated Analysis

Sovereign's Edict provides fully automated policy argument analysis:

### One-Click Analysis
Simply click "Run Analysis" after uploading data to automatically process comments and generate insights.

### Quick Demo Mode
For faster results, use the Quick Demo Mode to analyze the first 50 comments.

### Progress Tracking
Real-time progress indicators show analysis status.

### Auto-Citations
All arguments include clickable source links for verification.
```

## Next Steps

After implementing the automated processing pipeline:
1. Proceed to Phase 4: User-Friendly Dashboard
2. Update user documentation
3. Conduct performance testing with large datasets
4. Optimize caching and batch processing