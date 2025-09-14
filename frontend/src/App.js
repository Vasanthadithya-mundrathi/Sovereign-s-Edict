import React, { useState } from 'react';
import './App.css';
import HeatmapVisualization from './components/HeatmapVisualization';
import ArgumentCluster from './components/ArgumentCluster';
import CitationPanel from './components/CitationPanel';
import AmendmentSuggestion from './components/AmendmentSuggestion';

function App() {
  const [activeTab, setActiveTab] = useState('upload');

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sovereign's Edict</h1>
        <p>An Actionable Intelligence Platform for Clause-Level Policy Argumentation</p>
      </header>

      <nav className="App-nav">
        <button 
          className={activeTab === 'upload' ? 'active' : ''}
          onClick={() => setActiveTab('upload')}
        >
          Upload Data
        </button>
        <button 
          className={activeTab === 'analyze' ? 'active' : ''}
          onClick={() => setActiveTab('analyze')}
        >
          Analyze
        </button>
        <button 
          className={activeTab === 'results' ? 'active' : ''}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
      </nav>

      <main className="App-main">
        {activeTab === 'upload' && <UploadTab />}
        {activeTab === 'analyze' && <AnalyzeTab />}
        {activeTab === 'results' && <ResultsTab />}
        {activeTab === 'dashboard' && <DashboardTab />}
      </main>
    </div>
  );
}

function UploadTab() {
  return (
    <div className="tab-content">
      <h2>Upload Policy Data</h2>
      <div className="upload-section">
        <h3>Upload Policy Document</h3>
        <input type="file" accept=".txt,.pdf" />
        <button>Upload Policy</button>
      </div>
      
      <div className="upload-section">
        <h3>Upload Comments</h3>
        <input type="file" accept=".csv,.json" />
        <button>Upload Comments</button>
      </div>
      
      <div className="upload-instructions">
        <h3>Upload Instructions</h3>
        <ul>
          <li>Policy documents should be in plain text (.txt) or PDF format</li>
          <li>Comments can be uploaded as CSV or JSON files</li>
          <li>CSV files should include columns: text, source, timestamp, policy_clause</li>
          <li>JSON files should be an array of objects with the same properties</li>
        </ul>
      </div>
    </div>
  );
}

function AnalyzeTab() {
  return (
    <div className="tab-content">
      <h2>Analysis</h2>
      <div className="analysis-controls">
        <button className="btn-primary">Run Analysis</button>
        <button className="btn-secondary">Run Advanced Analysis</button>
      </div>
      <div className="analysis-status">
        <p>Status: Ready to analyze</p>
        <div className="progress-info">
          <p>Estimated time: 2-5 minutes for small datasets</p>
        </div>
      </div>
      
      <div className="analysis-options">
        <h3>Analysis Options</h3>
        <div className="option-group">
          <label>
            <input type="checkbox" defaultChecked /> 
            Argument Extraction
          </label>
          <label>
            <input type="checkbox" defaultChecked /> 
            Theme Clustering
          </label>
          <label>
            <input type="checkbox" defaultChecked /> 
            Sentiment Analysis
          </label>
          <label>
            <input type="checkbox" defaultChecked /> 
            Citation Matching
          </label>
        </div>
      </div>
    </div>
  );
}

function ResultsTab() {
  return (
    <div className="tab-content">
      <h2>Analysis Results</h2>
      <div className="results-summary">
        <div className="result-card">
          <h3>Total Arguments</h3>
          <p>67</p>
          <div className="trend positive">↑ 12% from last analysis</div>
        </div>
        <div className="result-card">
          <h3>Clauses Analyzed</h3>
          <p>12</p>
          <div className="trend neutral">No change</div>
        </div>
        <div className="result-card">
          <h3>Suggestions</h3>
          <p>8</p>
          <div className="trend positive">↑ 3 new</div>
        </div>
        <div className="result-card">
          <h3>Citations Matched</h3>
          <p>24</p>
          <div className="trend positive">↑ 5</div>
        </div>
      </div>
      
      <div className="results-details">
        <h3>Key Insights</h3>
        <div className="insight-list">
          <div className="insight-item high">
            <h4>High Concern: Privacy Issues</h4>
            <p>Sections 7(a) and 7(b) have generated 35% of all objections</p>
          </div>
          <div className="insight-item medium">
            <h4>Mixed Feedback: International Transfers</h4>
            <p>Section 8 has both strong support and significant concerns</p>
          </div>
          <div className="insight-item low">
            <h4>Strong Support: User Rights</h4>
            <p>Section 5 has 82% positive sentiment</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function DashboardTab() {
  return (
    <div className="tab-content">
      <h2>Policy Dashboard</h2>
      <div className="dashboard-content">
        <HeatmapVisualization />
        <ArgumentCluster />
        <CitationPanel />
        <AmendmentSuggestion />
      </div>
    </div>
  );
}

export default App;