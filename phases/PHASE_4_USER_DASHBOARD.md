# Phase 4: User-Friendly Dashboard Implementation

## Overview
Create a visual-first dashboard with policy structure visualization, heatmaps, clusters, sample comments, and counterpoint suggestions.

## Implementation Steps

### 1. Backend Implementation

#### Step 1: Enhance Results API Endpoints

Update `backend/main.py` to provide more detailed results:

```python
@app.get("/results/dashboard")
async def get_dashboard_data():
    """
    Get comprehensive dashboard data
    """
    if not stored_data.get("analysis_results"):
        raise HTTPException(status_code=400, detail="No analysis completed")
    
    # Get policy document
    policy = stored_data["policies"][0] if stored_data["policies"] else None
    
    # Get clause-level analysis
    clause_analysis = {}
    for argument in stored_data["arguments"]:
        clause = argument.clause
        if clause not in clause_analysis:
            clause_analysis[clause] = {
                "support_count": 0,
                "objection_count": 0,
                "total_arguments": 0,
                "themes": set(),
                "sample_comments": [],
                "confidence_score": 0
            }
        
        clause_analysis[clause]["total_arguments"] += 1
        if argument.type == "support":
            clause_analysis[clause]["support_count"] += 1
        else:
            clause_analysis[clause]["objection_count"] += 1
            
        # Add themes
        for theme in argument.themes:
            clause_analysis[clause]["themes"].add(theme)
        
        # Add sample comments (limit to 3 per clause)
        if len(clause_analysis[clause]["sample_comments"]) < 3:
            # Find the source comment
            source_comment = next((c for c in stored_data["comments"] if c.id == argument.source_comment), None)
            if source_comment and source_comment.text not in [sc["text"] for sc in clause_analysis[clause]["sample_comments"]]:
                clause_analysis[clause]["sample_comments"].append({
                    "text": source_comment.text[:100] + "..." if len(source_comment.text) > 100 else source_comment.text,
                    "source": source_comment.source
                })
        
        # Update confidence score (average)
        clause_analysis[clause]["confidence_score"] = (
            (clause_analysis[clause]["confidence_score"] * (clause_analysis[clause]["total_arguments"] - 1) + 
             argument.confidence) / clause_analysis[clause]["total_arguments"]
        )
    
    # Convert sets to lists for JSON serialization
    for clause in clause_analysis:
        clause_analysis[clause]["themes"] = list(clause_analysis[clause]["themes"])
        # Calculate controversy score (higher when support and objection counts are close)
        support = clause_analysis[clause]["support_count"]
        objection = clause_analysis[clause]["objection_count"]
        total = support + objection
        clause_analysis[clause]["controversy_score"] = (
            1 - abs(support - objection) / total if total > 0 else 0
        )
        # Calculate热度 score (based on total arguments)
        clause_analysis[clause]["heat_score"] = total
    
    return {
        "policy": policy.dict() if policy else None,
        "clause_analysis": clause_analysis,
        "total_arguments": len(stored_data["arguments"]),
        "suggestions": stored_data["analysis_results"].get("suggestions", [])[:5],  # Top 5 suggestions
        "processing_time": stored_data["analysis_results"].get("completed_at", 0) - stored_data["analysis_results"].get("started_at", 0)
    }

@app.get("/results/clause/{clause_id}/details")
async def get_clause_details(clause_id: str):
    """
    Get detailed analysis for a specific clause
    """
    # Find arguments for this clause
    clause_arguments = [arg for arg in stored_data["arguments"] if arg.clause == clause_id]
    
    if not clause_arguments:
        raise HTTPException(status_code=404, detail="Clause not found")
    
    # Group by theme
    theme_arguments = {}
    for arg in clause_arguments:
        for theme in arg.themes:
            if theme not in theme_arguments:
                theme_arguments[theme] = []
            theme_arguments[theme].append({
                "id": arg.id,
                "text": arg.text,
                "type": arg.type,
                "confidence": arg.confidence,
                "citations": arg.citations
            })
    
    # Get sample comments
    sample_comments = []
    for arg in clause_arguments[:5]:  # Limit to 5 arguments
        source_comment = next((c for c in stored_data["comments"] if c.id == arg.source_comment), None)
        if source_comment:
            sample_comments.append({
                "text": source_comment.text,
                "source": source_comment.source,
                "timestamp": source_comment.timestamp
            })
    
    # Get related citations
    all_citations = []
    for arg in clause_arguments:
        for citation_id in arg.citations:
            citation = next((c for c in stored_data["citations"] if c.id == citation_id), None)
            if citation and citation not in all_citations:
                all_citations.append(citation)
    
    return {
        "clause_id": clause_id,
        "total_arguments": len(clause_arguments),
        "support_count": len([arg for arg in clause_arguments if arg.type == "support"]),
        "objection_count": len([arg for arg in clause_arguments if arg.type == "objection"]),
        "themes": theme_arguments,
        "sample_comments": sample_comments,
        "citations": [c.dict() for c in all_citations[:10]],  # Limit to 10 citations
        "confidence_score": sum(arg.confidence for arg in clause_arguments) / len(clause_arguments)
    }
```

### 2. Frontend Implementation

#### Step 1: Create New Dashboard Components

Create `frontend/src/components/PolicyViewer.js`:

```javascript
import React, { useState } from 'react';

const PolicyViewer = ({ policy, clauseAnalysis, onClauseSelect }) => {
  const [expandedClause, setExpandedClause] = useState(null);

  if (!policy) {
    return <div className="policy-viewer">No policy document available</div>;
  }

  // Split policy content into clauses (simplified)
  const clauses = policy.content.split('\n\n').map((text, index) => ({
    id: `clause_${index + 1}`,
    text: text.trim(),
    analysis: clauseAnalysis[`clause_${index + 1}`] || {
      support_count: 0,
      objection_count: 0,
      total_arguments: 0,
      controversy_score: 0,
      heat_score: 0
    }
  }));

  const getClauseHeatColor = (analysis) => {
    const score = analysis.heat_score || 0;
    if (score === 0) return '#f0f0f0';
    if (score < 5) return '#d0e6ff';
    if (score < 10) return '#80b3ff';
    if (score < 20) return '#3385ff';
    return '#0052cc';
  };

  const getControversyLevel = (analysis) => {
    const score = analysis.controversy_score || 0;
    if (score < 0.3) return 'Low';
    if (score < 0.6) return 'Medium';
    return 'High';
  };

  return (
    <div className="policy-viewer">
      <h2>{policy.title}</h2>
      <div className="clauses-container">
        {clauses.map((clause, index) => (
          <div 
            key={clause.id}
            className={`clause-tile ${expandedClause === clause.id ? 'expanded' : ''}`}
            style={{ borderLeft: `5px solid ${getClauseHeatColor(clause.analysis)}` }}
            onClick={() => {
              setExpandedClause(expandedClause === clause.id ? null : clause.id);
              if (onClauseSelect) onClauseSelect(clause.id);
            }}
          >
            <div className="clause-header">
              <h3>Clause {index + 1}</h3>
              <div className="clause-stats">
                <span className="stat heat-score">
                  🔥 {clause.analysis.heat_score || 0}
                </span>
                <span className="stat controversy">
                  ⚖️ {getControversyLevel(clause.analysis)}
                </span>
              </div>
            </div>
            <div className="clause-content">
              <p>{clause.text.substring(0, 150)}{clause.text.length > 150 ? '...' : ''}</p>
            </div>
            {expandedClause === clause.id && (
              <div className="clause-details">
                <div className="argument-stats">
                  <span className="support">Support: {clause.analysis.support_count}</span>
                  <span className="objection">Objection: {clause.analysis.objection_count}</span>
                  <span className="total">Total: {clause.analysis.total_arguments}</span>
                </div>
                <div className="themes">
                  <strong>Themes:</strong> {clause.analysis.themes?.join(', ') || 'None'}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PolicyViewer;
```

Create `frontend/src/components/HeatmapVisualization.js` (enhanced version):

```javascript
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const HeatmapVisualization = ({ clauseAnalysis }) => {
  // Convert clause analysis to chart data
  const chartData = Object.entries(clauseAnalysis || {}).map(([clauseId, analysis]) => ({
    clause: clauseId,
    support: analysis.support_count || 0,
    objection: analysis.objection_count || 0,
    total: analysis.total_arguments || 0,
    controversy: Math.round((analysis.controversy_score || 0) * 100),
    heat: analysis.heat_score || 0
  }));

  return (
    <div className="heatmap-visualization">
      <h3>Clause-Level Analysis Heatmap</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="clause" angle={-45} textAnchor="end" height={60} />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => {
                if (name === 'controversy') return [`${value}%`, 'Controversy'];
                if (name === 'heat') return [value, 'Heat Score'];
                return [value, name.charAt(0).toUpperCase() + name.slice(1)];
              }}
            />
            <Legend />
            <Bar dataKey="support" name="Support" fill="#4CAF50" />
            <Bar dataKey="objection" name="Objection" fill="#F44336" />
            <Bar dataKey="controversy" name="Controversy %" fill="#FF9800" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="heatmap-legend">
        <h4>Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="color-box" style={{backgroundColor: '#4CAF50'}}></div>
            <span>Support Arguments</span>
          </div>
          <div className="legend-item">
            <div className="color-box" style={{backgroundColor: '#F44336'}}></div>
            <span>Objection Arguments</span>
          </div>
          <div className="legend-item">
            <div className="color-box" style={{backgroundColor: '#FF9800'}}></div>
            <span>Controversy Level (%)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeatmapVisualization;
```

Create `frontend/src/components/ArgumentCluster.js` (enhanced version):

```javascript
import React, { useState } from 'react';

const ArgumentCluster = ({ clauseDetails }) => {
  const [selectedTheme, setSelectedTheme] = useState(null);

  if (!clauseDetails) {
    return <div className="argument-cluster">Select a clause to view arguments</div>;
  }

  const themes = Object.keys(clauseDetails.themes || {});

  return (
    <div className="argument-cluster">
      <h3>Argument Clusters for Clause {clauseDetails.clause_id}</h3>
      
      <div className="theme-selector">
        <h4>Themes:</h4>
        <div className="theme-buttons">
          {themes.map(theme => (
            <button
              key={theme}
              className={`theme-button ${selectedTheme === theme ? 'active' : ''}`}
              onClick={() => setSelectedTheme(selectedTheme === theme ? null : theme)}
            >
              {theme}
            </button>
          ))}
        </div>
      </div>
      
      <div className="arguments-container">
        {selectedTheme ? (
          <ThemeArguments 
            theme={selectedTheme} 
            arguments={clauseDetails.themes[selectedTheme] || []} 
          />
        ) : (
          <AllArguments clauseDetails={clauseDetails} />
        )}
      </div>
    </div>
  );
};

const ThemeArguments = ({ theme, arguments: args }) => {
  return (
    <div className="theme-arguments">
      <h4>Arguments for Theme: {theme}</h4>
      {args.map((arg, index) => (
        <div key={arg.id} className={`argument-card ${arg.type}`}>
          <div className="argument-header">
            <span className={`type-badge ${arg.type}`}>
              {arg.type.toUpperCase()}
            </span>
            <span className="confidence">
              Confidence: {arg.confidence}%
            </span>
          </div>
          <p className="argument-text">{arg.text}</p>
          <div className="argument-footer">
            <span className="argument-id">ID: {arg.id}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

const AllArguments = ({ clauseDetails }) => {
  const allArguments = [];
  Object.values(clauseDetails.themes || {}).forEach(themeArgs => {
    allArguments.push(...themeArgs);
  });

  return (
    <div className="all-arguments">
      <h4>All Arguments ({clauseDetails.total_arguments})</h4>
      <div className="argument-stats">
        <span className="stat support">Support: {clauseDetails.support_count}</span>
        <span className="stat objection">Objection: {clauseDetails.objection_count}</span>
      </div>
      {allArguments.map((arg, index) => (
        <div key={arg.id} className={`argument-card ${arg.type}`}>
          <div className="argument-header">
            <span className={`type-badge ${arg.type}`}>
              {arg.type.toUpperCase()}
            </span>
            <span className="confidence">
              Confidence: {arg.confidence}%
            </span>
          </div>
          <p className="argument-text">{arg.text}</p>
          <div className="argument-footer">
            <span className="argument-id">ID: {arg.id}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ArgumentCluster;
```

Create `frontend/src/components/SampleComments.js`:

```javascript
import React from 'react';

const SampleComments = ({ comments }) => {
  if (!comments || comments.length === 0) {
    return <div className="sample-comments">No sample comments available</div>;
  }

  return (
    <div className="sample-comments">
      <h3>Real People Said...</h3>
      <div className="comments-container">
        {comments.map((comment, index) => (
          <div key={index} className="comment-card">
            <p className="comment-text">"{comment.text}"</p>
            <div className="comment-source">
              Source: {comment.source}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SampleComments;
```

Create `frontend/src/components/CounterpointSuggestions.js`:

```javascript
import React from 'react';

const CounterpointSuggestions = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) {
    return <div className="counterpoint-suggestions">No suggestions available</div>;
  }

  return (
    <div className="counterpoint-suggestions">
      <h3>Suggested Responses</h3>
      <div className="suggestions-container">
        {suggestions.map((suggestion, index) => (
          <div key={suggestion.id} className="suggestion-card">
            <div className="suggestion-header">
              <span className="suggestion-type">{suggestion.type.replace('_', ' ')}</span>
              <span className="suggestion-clause">Clause: {suggestion.clause}</span>
            </div>
            <h4 className="suggestion-summary">{suggestion.summary}</h4>
            <p className="suggestion-details">{suggestion.details}</p>
            <div className="suggestion-change">
              <strong>Suggested Change:</strong> {suggestion.suggested_change}
            </div>
            {suggestion.citations && suggestion.citations.length > 0 && (
              <div className="suggestion-citations">
                <strong>Related Citations:</strong>
                <ul>
                  {suggestion.citations.slice(0, 3).map((citation, idx) => (
                    <li key={idx}>
                      <a href={citation.url} target="_blank" rel="noopener noreferrer">
                        {citation.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="suggestion-confidence">
              Confidence: {Math.round(suggestion.confidence * 100)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CounterpointSuggestions;
```

#### Step 2: Update DashboardTab Component

Update `frontend/src/App.js` DashboardTab component:

```javascript
// Add new imports at the top
import PolicyViewer from './components/PolicyViewer';
import SampleComments from './components/SampleComments';
import CounterpointSuggestions from './components/CounterpointSuggestions';

function DashboardTab() {
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedClause, setSelectedClause] = useState(null);
  const [clauseDetails, setClauseDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/results/dashboard');
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchClauseDetails = async (clauseId) => {
    try {
      const response = await fetch(`http://localhost:8000/results/clause/${clauseId}/details`);
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setClauseDetails(data);
    } catch (error) {
      console.error('Failed to fetch clause details:', error);
    }
  };

  const handleClauseSelect = (clauseId) => {
    setSelectedClause(clauseId);
    fetchClauseDetails(clauseId);
  };

  if (loading) {
    return <div className="tab-content">Loading dashboard data...</div>;
  }

  if (!dashboardData) {
    return <div className="tab-content">No dashboard data available. Run an analysis first.</div>;
  }

  return (
    <div className="tab-content">
      <h2>Policy Dashboard</h2>
      
      <div className="dashboard-layout">
        <div className="dashboard-main">
          <PolicyViewer 
            policy={dashboardData.policy}
            clauseAnalysis={dashboardData.clause_analysis}
            onClauseSelect={handleClauseSelect}
          />
          
          {selectedClause && (
            <div className="clause-details-panel">
              <h3>Clause Details: {selectedClause}</h3>
              <ArgumentCluster clauseDetails={clauseDetails} />
              {clauseDetails && (
                <SampleComments comments={clauseDetails.sample_comments} />
              )}
            </div>
          )}
        </div>
        
        <div className="dashboard-sidebar">
          <div className="dashboard-summary">
            <h3>Analysis Summary</h3>
            <div className="summary-stats">
              <div className="stat-card">
                <h4>Total Arguments</h4>
                <p>{dashboardData.total_arguments}</p>
              </div>
              <div className="stat-card">
                <h4>Clauses Analyzed</h4>
                <p>{Object.keys(dashboardData.clause_analysis || {}).length}</p>
              </div>
              <div className="stat-card">
                <h4>Suggestions</h4>
                <p>{dashboardData.suggestions.length}</p>
              </div>
            </div>
          </div>
          
          <CounterpointSuggestions suggestions={dashboardData.suggestions} />
          
          <HeatmapVisualization clauseAnalysis={dashboardData.clause_analysis} />
        </div>
      </div>
    </div>
  );
}
```

#### Step 3: Add CSS for New Components

Update `frontend/src/App.css` with new styles:

```css
.dashboard-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.dashboard-main {
  flex: 3;
  overflow-y: auto;
}

.dashboard-sidebar {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.policy-viewer {
  margin-bottom: 20px;
}

.policy-viewer h2 {
  margin-top: 0;
  color: #333;
}

.clauses-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.clause-tile {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fff;
}

.clause-tile:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.clause-tile.expanded {
  background-color: #f8f9fa;
}

.clause-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.clause-header h3 {
  margin: 0;
  color: #333;
}

.clause-stats {
  display: flex;
  gap: 10px;
}

.stat {
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 12px;
  background-color: #e9ecef;
}

.heat-score {
  background-color: #ffeaa7;
}

.controversy {
  background-color: #fd79a8;
  color: white;
}

.clause-content p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.clause-details {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.argument-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.argument-stats .support {
  color: #28a745;
  font-weight: bold;
}

.argument-stats .objection {
  color: #dc3545;
  font-weight: bold;
}

.argument-stats .total {
  color: #007bff;
  font-weight: bold;
}

.themes {
  font-size: 14px;
  color: #666;
}

.heatmap-visualization {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.heatmap-visualization h3 {
  margin-top: 0;
  color: #333;
}

.chart-container {
  height: 400px;
  margin: 20px 0;
}

.heatmap-legend {
  margin-top: 20px;
}

.heatmap-legend h4 {
  margin-top: 0;
  color: #333;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.argument-cluster {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.argument-cluster h3 {
  margin-top: 0;
  color: #333;
}

.theme-selector {
  margin-bottom: 20px;
}

.theme-selector h4 {
  margin-bottom: 10px;
  color: #333;
}

.theme-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.theme-button {
  background-color: #e9ecef;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.theme-button:hover {
  background-color: #dee2e6;
}

.theme-button.active {
  background-color: #007bff;
  color: white;
}

.argument-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #f8f9fa;
}

.argument-card.support {
  border-left: 5px solid #28a745;
}

.argument-card.objection {
  border-left: 5px solid #dc3545;
}

.argument-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.type-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.type-badge.support {
  background-color: #d4edda;
  color: #155724;
}

.type-badge.objection {
  background-color: #f8d7da;
  color: #721c24;
}

.confidence {
  font-size: 12px;
  color: #666;
}

.argument-text {
  margin: 10px 0;
  line-height: 1.5;
  color: #333;
}

.argument-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.sample-comments {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.sample-comments h3 {
  margin-top: 0;
  color: #333;
}

.comments-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background-color: #f8f9fa;
}

.comment-text {
  margin: 0 0 10px 0;
  font-style: italic;
  color: #555;
  line-height: 1.5;
}

.comment-source {
  font-size: 12px;
  color: #666;
}

.counterpoint-suggestions {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.counterpoint-suggestions h3 {
  margin-top: 0;
  color: #333;
}

.suggestions-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.suggestion-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff8e1;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.suggestion-type {
  background-color: #ffc107;
  color: #212529;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.suggestion-clause {
  font-size: 12px;
  color: #666;
}

.suggestion-summary {
  margin: 10px 0;
  color: #333;
}

.suggestion-details {
  margin: 10px 0;
  color: #555;
  line-height: 1.5;
}

.suggestion-change {
  margin: 10px 0;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
  font-size: 14px;
}

.suggestion-citations {
  margin: 10px 0;
}

.suggestion-citations ul {
  margin: 5px 0;
  padding-left: 20px;
}

.suggestion-citations li {
  margin-bottom: 5px;
}

.suggestion-citations a {
  color: #007bff;
  text-decoration: none;
}

.suggestion-citations a:hover {
  text-decoration: underline;
}

.suggestion-confidence {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
  text-align: right;
}

.dashboard-summary {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-summary h3 {
  margin-top: 0;
  color: #333;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  background-color: #f8f9fa;
}

.stat-card h4 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.stat-card p {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
}

.clause-details-panel {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
```

### 3. Install Required Frontend Dependencies

Install Recharts for data visualization:

```bash
cd frontend
npm install recharts
```

### 4. Testing and Verification

#### Step 1: Test Dashboard API Endpoints
```bash
# Test dashboard data endpoint
curl "http://localhost:8000/results/dashboard"

# Test clause details endpoint
curl "http://localhost:8000/results/clause/clause_1/details"
```

#### Step 2: Test Frontend Components
1. Start the backend server
2. Start the frontend development server
3. Navigate to the Dashboard tab
4. Verify that:
   - Policy document is displayed with clause tiles
   - Heatmap visualization shows properly
   - Clicking on clauses shows details
   - Argument clusters display correctly
   - Sample comments are shown
   - Counterpoint suggestions are displayed

### 5. Performance Optimization

#### For Large Datasets:
1. Implement virtual scrolling for long lists
2. Add pagination for arguments and comments
3. Use memoization for expensive calculations
4. Optimize rendering with React.memo and useMemo

### 6. Accessibility Improvements

#### Implementation:
1. Add proper ARIA labels
2. Ensure keyboard navigation works
3. Add screen reader support
4. Implement proper color contrast

### 7. Documentation Updates

Update the README.md to include information about the dashboard:

```markdown
## User-Friendly Dashboard

Sovereign's Edict features a comprehensive dashboard for visualizing policy analysis:

### Policy Structure View
See the policy document with visual indicators showing controversy levels and argument density for each clause.

### Heatmap Visualization
Interactive charts showing support vs. objection arguments across all clauses.

### Argument Clustering
Grouped arguments by themes with confidence scoring.

### Sample Comments
Real examples of public comments for each argument cluster.

### Counterpoint Suggestions
Data-backed policy amendment suggestions with citations.
```

## Next Steps

After implementing the user-friendly dashboard:
1. Proceed to Phase 5: Explain Everything Mode
2. Update user documentation with dashboard screenshots
3. Conduct usability testing with non-technical users
4. Optimize performance for large datasets