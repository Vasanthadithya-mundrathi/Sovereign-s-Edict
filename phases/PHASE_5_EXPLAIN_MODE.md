# Phase 5: Explain Everything Mode Implementation

## Overview
Implement tooltips, glossary, walkthrough guide, and plain-language explanations throughout the application.

## Implementation Steps

### 1. Backend Implementation

#### Step 1: Create Explanation API

Create `backend/api/explanation.py`:

```python
"""
Explanation API for Sovereign's Edict
"""
from fastapi import APIRouter
from typing import Dict, List

router = APIRouter(prefix="/explain")

# Explanation database
EXPLANATIONS = {
    "cluster": {
        "title": "Argument Cluster",
        "definition": "A group of similar arguments that share common themes or points.",
        "why_important": "Clusters help identify the main themes in public feedback, making it easier to understand overall sentiment.",
        "how_calculated": "Arguments are grouped using natural language processing techniques that identify semantic similarities."
    },
    "clause": {
        "title": "Policy Clause",
        "definition": "A specific section or provision in a policy document.",
        "why_important": "Analyzing feedback at the clause level helps policymakers understand which specific parts of a policy are controversial or well-received.",
        "how_calculated": "Clauses are identified by section headings or natural language processing techniques that segment policy text."
    },
    "controversy_score": {
        "title": "Controversy Score",
        "definition": "A numerical value indicating how divided public opinion is on a specific clause.",
        "why_important": "High controversy scores indicate areas that may need revision or additional public consultation.",
        "how_calculated": "Calculated as 1 - (|support_arguments - objection_arguments| / total_arguments). Higher scores mean more balanced support and objection."
    },
    "heat_score": {
        "title": "Heat Score",
        "definition": "A measure of how much public attention a clause has received.",
        "why_important": "High heat scores indicate clauses that generated significant public discussion.",
        "how_calculated": "Based on the total number of arguments (support + objection) for a clause."
    },
    "confidence_score": {
        "title": "Confidence Score",
        "definition": "How certain the AI is about the accuracy of an analysis.",
        "why_important": "Helps users understand the reliability of insights and identify areas that may need manual review.",
        "how_calculated": "Based on multiple factors including argument clarity, citation quality, and semantic coherence."
    },
    "citation": {
        "title": "Citation",
        "definition": "A reference to a law, regulation, or other document that supports or relates to an argument.",
        "why_important": "Citations provide evidence for arguments and help policymakers verify claims.",
        "how_calculated": "Identified through natural language processing that matches text to known legal documents and precedents."
    },
    "gemini_api": {
        "title": "Gemini AI",
        "definition": "Google's advanced artificial intelligence model used for natural language understanding.",
        "why_important": "Gemini helps extract nuanced arguments and identify complex themes in public feedback.",
        "how_calculated": "Arguments are processed through prompts designed to extract structured information while preserving context and nuance."
    }
}

@router.get("/concept/{concept_id}")
async def get_concept_explanation(concept_id: str):
    """
    Get explanation for a specific concept
    """
    if concept_id not in EXPLANATIONS:
        return {"error": "Concept not found"}
    
    return EXPLANATIONS[concept_id]

@router.get("/glossary")
async def get_glossary():
    """
    Get complete glossary of terms
    """
    return {
        "terms": [
            {
                "id": key,
                "title": value["title"],
                "definition": value["definition"]
            }
            for key, value in EXPLANATIONS.items()
        ]
    }

@router.get("/walkthrough")
async def get_walkthrough():
    """
    Get step-by-step walkthrough guide
    """
    return {
        "steps": [
            {
                "step": 1,
                "title": "Upload Data",
                "description": "Start by uploading policy documents and public comments using the Upload tab.",
                "details": "You can paste YouTube links, web URLs, or upload CSV/Excel/JSON files containing comments."
            },
            {
                "step": 2,
                "title": "Run Analysis",
                "description": "Click 'Run Analysis' to process your data and extract insights.",
                "details": "The system will automatically identify arguments, group them by theme, and match them to policy clauses."
            },
            {
                "step": 3,
                "title": "Explore Dashboard",
                "description": "View the results in the Dashboard tab with visualizations and detailed analysis.",
                "details": "Click on any clause to see detailed argument clusters, sample comments, and suggested responses."
            },
            {
                "step": 4,
                "title": "Review Suggestions",
                "description": "Check the amendment suggestions generated based on the analysis.",
                "details": "Each suggestion includes supporting citations and a confidence score."
            },
            {
                "step": 5,
                "title": "Export Results",
                "description": "Download your analysis as a PDF report for sharing with colleagues.",
                "details": "The report includes all visualizations, argument clusters, and suggestions."
            }
        ]
    }
```

#### Step 2: Register Explanation Router

Update `backend/main.py`:

```python
# Add import
from .api import explanation

# Register router
app.include_router(explanation.router)
```

### 2. Frontend Implementation

#### Step 1: Create Explanation Components

Create `frontend/src/components/Tooltip.js`:

```javascript
import React, { useState } from 'react';

const Tooltip = ({ children, content, position = 'top' }) => {
  const [visible, setVisible] = useState(false);
  const [clicked, setClicked] = useState(false);

  const showTooltip = () => {
    setVisible(true);
  };

  const hideTooltip = () => {
    if (!clicked) {
      setVisible(false);
    }
  };

  const toggleTooltip = () => {
    setClicked(!clicked);
    setVisible(!clicked);
  };

  return (
    <div className="tooltip-container">
      <div 
        className="tooltip-trigger"
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onClick={toggleTooltip}
      >
        {children}
      </div>
      {visible && (
        <div className={`tooltip tooltip-${position}`}>
          <div className="tooltip-content">
            {typeof content === 'string' ? <p>{content}</p> : content}
          </div>
          <div className="tooltip-arrow"></div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;
```

Create `frontend/src/components/Glossary.js`:

```javascript
import React, { useState, useEffect } from 'react';

const Glossary = () => {
  const [glossary, setGlossary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchGlossary();
  }, []);

  const fetchGlossary = async () => {
    try {
      const response = await fetch('http://localhost:8000/explain/glossary');
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setGlossary(data.terms);
    } catch (error) {
      console.error('Failed to fetch glossary:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTerms = glossary.filter(term =>
    term.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    term.definition.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="glossary">Loading glossary...</div>;
  }

  return (
    <div className="glossary">
      <h2>Glossary of Terms</h2>
      
      <div className="glossary-search">
        <input
          type="text"
          placeholder="Search terms..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      
      <div className="glossary-terms">
        {filteredTerms.length > 0 ? (
          filteredTerms.map((term) => (
            <div key={term.id} className="glossary-term">
              <h3>{term.title}</h3>
              <p>{term.definition}</p>
              <button 
                className="explain-button"
                onClick={() => {
                  // Fetch detailed explanation
                  fetch(`http://localhost:8000/explain/concept/${term.id}`)
                    .then(response => response.json())
                    .then(data => {
                      if (!data.error) {
                        alert(`${data.title}\n\nDefinition: ${data.definition}\n\nWhy Important: ${data.why_important}\n\nHow Calculated: ${data.how_calculated}`);
                      }
                    });
                }}
              >
                More Details
              </button>
            </div>
          ))
        ) : (
          <p>No terms found matching your search.</p>
        )}
      </div>
    </div>
  );
};

export default Glossary;
```

Create `frontend/src/components/Walkthrough.js`:

```javascript
import React, { useState, useEffect } from 'react';

const Walkthrough = ({ onComplete }) => {
  const [steps, setSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWalkthrough();
  }, []);

  const fetchWalkthrough = async () => {
    try {
      const response = await fetch('http://localhost:8000/explain/walkthrough');
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setSteps(data.steps);
    } catch (error) {
      console.error('Failed to fetch walkthrough:', error);
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Complete walkthrough
      if (onComplete) onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (loading) {
    return <div className="walkthrough">Loading walkthrough...</div>;
  }

  if (steps.length === 0) {
    return <div className="walkthrough">No walkthrough available.</div>;
  }

  const step = steps[currentStep];

  return (
    <div className="walkthrough-overlay">
      <div className="walkthrough-modal">
        <div className="walkthrough-header">
          <h2>Getting Started Guide</h2>
          <span className="step-indicator">
            Step {step.step} of {steps.length}
          </span>
        </div>
        
        <div className="walkthrough-content">
          <h3>{step.title}</h3>
          <p>{step.description}</p>
          <div className="walkthrough-details">
            <p><strong>Details:</strong> {step.details}</p>
          </div>
        </div>
        
        <div className="walkthrough-navigation">
          <button 
            onClick={prevStep}
            disabled={currentStep === 0}
            className="nav-button prev-button"
          >
            Previous
          </button>
          <button 
            onClick={nextStep}
            className="nav-button next-button"
          >
            {currentStep === steps.length - 1 ? 'Finish' : 'Next'}
          </button>
        </div>
        
        <div className="walkthrough-progress">
          <div 
            className="progress-bar"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default Walkthrough;
```

#### Step 2: Add Tooltips Throughout the Application

Update `frontend/src/App.js` to add tooltips to key elements:

```javascript
// Add import
import Tooltip from './components/Tooltip';

// Update key components with tooltips

function UploadTab() {
  return (
    <div className="tab-content">
      <h2>
        Smart Data Ingestion
        <Tooltip content="Upload policy documents and public comments from various sources">
          <span className="help-icon">?</span>
        </Tooltip>
      </h2>
      {/* ... rest of component with tooltips ... */}
    </div>
  );
}

function AnalyzeTab() {
  return (
    <div className="tab-content">
      <h2>
        Automated Analysis
        <Tooltip content="Process uploaded data to extract arguments and generate insights">
          <span className="help-icon">?</span>
        </Tooltip>
      </h2>
      {/* ... rest of component with tooltips ... */}
    </div>
  );
}

function ResultsTab() {
  return (
    <div className="tab-content">
      <h2>
        Analysis Results
        <Tooltip content="View extracted arguments, clause analysis, and policy suggestions">
          <span className="help-icon">?</span>
        </Tooltip>
      </h2>
      {/* ... rest of component with tooltips ... */}
    </div>
  );
}

function DashboardTab() {
  return (
    <div className="tab-content">
      <h2>
        Policy Dashboard
        <Tooltip content="Interactive visualization of policy analysis results">
          <span className="help-icon">?</span>
        </Tooltip>
      </h2>
      {/* ... rest of component with tooltips ... */}
    </div>
  );
}
```

#### Step 3: Add Glossary and Walkthrough Pages

Update `frontend/src/App.js` to include new pages:

```javascript
// Add new state for walkthrough
const [showWalkthrough, setShowWalkthrough] = useState(false);

// Add new tab buttons
<nav className="App-nav">
  {/* ... existing buttons ... */}
  <button 
    className={activeTab === 'glossary' ? 'active' : ''}
    onClick={() => setActiveTab('glossary')}
  >
    Glossary
  </button>
  <button 
    className={activeTab === 'help' ? 'active' : ''}
    onClick={() => setShowWalkthrough(true)}
  >
    Help
  </button>
</nav>

// Add new tab content
{activeTab === 'glossary' && <Glossary />}
{showWalkthrough && (
  <Walkthrough onComplete={() => setShowWalkthrough(false)} />
)}

// Update main content to handle walkthrough
<main className="App-main">
  {!showWalkthrough && (
    <>
      {activeTab === 'upload' && <UploadTab />}
      {activeTab === 'analyze' && <AnalyzeTab />}
      {activeTab === 'results' && <ResultsTab />}
      {activeTab === 'dashboard' && <DashboardTab />}
      {activeTab === 'glossary' && <Glossary />}
    </>
  )}
  {showWalkthrough && (
    <Walkthrough onComplete={() => setShowWalkthrough(false)} />
  )}
</main>
```

#### Step 4: Add CSS for Explanation Components

Update `frontend/src/App.css`:

```css
/* Tooltip Styles */
.tooltip-container {
  position: relative;
  display: inline-block;
}

.tooltip-trigger {
  cursor: help;
  border-bottom: 1px dotted #007bff;
}

.help-icon {
  display: inline-block;
  width: 18px;
  height: 18px;
  background-color: #007bff;
  color: white;
  border-radius: 50%;
  text-align: center;
  font-size: 12px;
  line-height: 18px;
  margin-left: 5px;
  cursor: help;
}

.tooltip {
  position: absolute;
  z-index: 1000;
  background-color: #333;
  color: white;
  padding: 10px;
  border-radius: 4px;
  max-width: 300px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.tooltip-top {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 5px;
}

.tooltip-bottom {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 5px;
}

.tooltip-left {
  top: 50%;
  right: 100%;
  transform: translateY(-50%);
  margin-right: 5px;
}

.tooltip-right {
  top: 50%;
  left: 100%;
  transform: translateY(-50%);
  margin-left: 5px;
}

.tooltip-content p {
  margin: 0;
  line-height: 1.4;
}

.tooltip-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border: 5px solid transparent;
}

.tooltip-top .tooltip-arrow {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: #333;
}

.tooltip-bottom .tooltip-arrow {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: #333;
}

.tooltip-left .tooltip-arrow {
  top: 50%;
  left: 100%;
  transform: translateY(-50%);
  border-left-color: #333;
}

.tooltip-right .tooltip-arrow {
  top: 50%;
  right: 100%;
  transform: translateY(-50%);
  border-right-color: #333;
}

/* Glossary Styles */
.glossary {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.glossary h2 {
  color: #333;
  margin-top: 0;
}

.glossary-search {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.glossary-terms {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.glossary-term {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: #f8f9fa;
}

.glossary-term h3 {
  margin-top: 0;
  color: #333;
}

.glossary-term p {
  margin: 10px 0;
  color: #666;
  line-height: 1.5;
}

.explain-button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
}

.explain-button:hover {
  background-color: #0056b3;
}

/* Walkthrough Styles */
.walkthrough-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.walkthrough-modal {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  position: relative;
}

.walkthrough-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.walkthrough-header h2 {
  margin: 0;
  color: #333;
}

.step-indicator {
  background-color: #007bff;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
}

.walkthrough-content h3 {
  color: #333;
  margin-top: 0;
}

.walkthrough-content p {
  color: #666;
  line-height: 1.5;
}

.walkthrough-details {
  background-color: #e9f7fe;
  border-left: 4px solid #007bff;
  padding: 15px;
  margin: 20px 0;
  border-radius: 0 4px 4px 0;
}

.walkthrough-details p {
  margin: 0;
  color: #333;
}

.walkthrough-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.nav-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.prev-button {
  background-color: #6c757d;
  color: white;
}

.prev-button:hover:not(:disabled) {
  background-color: #5a6268;
}

.prev-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.next-button {
  background-color: #007bff;
  color: white;
}

.next-button:hover {
  background-color: #0056b3;
}

.walkthrough-progress {
  height: 6px;
  background-color: #e9ecef;
  border-radius: 3px;
  margin-top: 20px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #007bff;
  transition: width 0.3s ease;
}
```

### 3. Context-Sensitive Help Implementation

#### Step 1: Add Help Icons to Key UI Elements

Update various components to include contextual help:

```javascript
// Example: Add help to clause tiles in PolicyViewer
<div className="clause-header">
  <h3>
    Clause {index + 1}
    <Tooltip content="A specific section of the policy document being analyzed">
      <span className="help-icon">?</span>
    </Tooltip>
  </h3>
  {/* ... */}
</div>

// Example: Add help to heatmap visualization
<h3>
  Clause-Level Analysis Heatmap
  <Tooltip content="Visual representation of argument distribution across policy clauses">
    <span className="help-icon">?</span>
  </Tooltip>
</h3>

// Example: Add help to argument cards
<div className="argument-header">
  <span className={`type-badge ${arg.type}`}>
    {arg.type.toUpperCase()}
  </span>
  <Tooltip content="Confidence score indicates how certain the AI is about this argument classification">
    <span className="confidence">
      Confidence: {arg.confidence}%
      <span className="help-icon">?</span>
    </span>
  </Tooltip>
</div>
```

### 4. Plain-Language UI Refinements

#### Step 1: Simplify Technical Terms

Update UI text to use plain language:

```javascript
// Instead of "Argument Extraction"
"Find Key Points"

// Instead of "Theme Clustering"
"Group Similar Ideas"

// Instead of "Sentiment Analysis"
"Understand Feelings"

// Instead of "Citation Matching"
"Find Supporting Evidence"
```

#### Step 2: Add Progress Indicators

Update analysis status messages:

```javascript
// Instead of "Processing..."
"We're analyzing your data..."

// Instead of "Completed"
"Analysis finished! Here's what we found:"
```

### 5. Testing and Verification

#### Step 1: Test Explanation API Endpoints
```bash
# Test concept explanation
curl "http://localhost:8000/explain/concept/cluster"

# Test glossary
curl "http://localhost:8000/explain/glossary"

# Test walkthrough
curl "http://localhost:8000/explain/walkthrough"
```

#### Step 2: Test Frontend Components
1. Start the backend server
2. Start the frontend development server
3. Navigate to the Glossary tab
4. Test the walkthrough guide
5. Hover over help icons to verify tooltips appear
6. Click tooltips to keep them open
7. Search in the glossary

### 6. Accessibility Improvements

#### Implementation:
1. Add proper ARIA labels to tooltips
2. Ensure keyboard navigation works for all help elements
3. Add screen reader support for explanations
4. Implement proper color contrast for all text

### 7. Documentation Updates

Update the README.md to include information about the explain mode:

```markdown
## Explain Everything Mode

Sovereign's Edict includes comprehensive help features to make the platform accessible to all users:

### Tooltips
Hover over any technical term to see a plain-language explanation.

### Glossary
Browse our complete glossary of policy analysis terms.

### Walkthrough Guide
Step-by-step tutorial for first-time users.

### Context-Sensitive Help
Get help specific to what you're working on.
```

## Next Steps

After implementing the explain everything mode:
1. Proceed to Phase 6: No-Setup Deployment
2. Update user documentation with screenshots of help features
3. Conduct usability testing with non-technical users
4. Gather feedback on clarity of explanations