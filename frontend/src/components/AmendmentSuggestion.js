import React, { useState } from 'react';
import './AmendmentSuggestion.css';

const AmendmentSuggestion = ({ data }) => {
  // Sample amendment suggestions
  const sampleSuggestions = [
    {
      id: 1,
      clause: "Section 7(a)",
      type: "objection_response",
      summary: "Address concerns regarding privacy and notification timing",
      details: "This clause has received significant objection, primarily concerning privacy and notification timing. Consider revising to address these concerns.",
      suggested_change: "Revise clause Section 7(a) to better address privacy and timing concerns by extending the notification period to 5 days and adding exceptions for good faith delays.",
      citations: [
        {
          id: 1,
          title: "Puttaswamy Judgment on Privacy Rights",
          source: "Supreme Court of India",
          type: "legal",
          summary: "Landmark judgment establishing privacy as a fundamental right under the Indian Constitution.",
          relevance_score: 0.98
        },
        {
          id: 2,
          title: "Data Breach Notification Requirements",
          source: "International Privacy Review",
          type: "expert",
          summary: "Analysis of notification requirements in data protection laws across jurisdictions.",
          relevance_score: 0.92
        }
      ],
      confidence: 0.9,
      impact: "high"
    },
    {
      id: 2,
      clause: "Section 7(b)",
      type: "objection_response",
      summary: "Refine individual notification requirements",
      details: "Concerns have been raised about unnecessary panic from individual notifications. Consider adding thresholds for notification requirements.",
      suggested_change: "Add a threshold of 100 affected individuals before individual notifications are required, with exceptions for high-risk breaches.",
      citations: [
        {
          id: 3,
          title: "GDPR Implementation Guidelines",
          source: "European Data Protection Board",
          type: "legal",
          summary: "Guidelines on implementing GDPR notification requirements.",
          relevance_score: 0.88
        }
      ],
      confidence: 0.82,
      impact: "medium"
    },
    {
      id: 3,
      clause: "Section 3",
      type: "objection_response",
      summary: "Clarify explicit consent definition",
      details: "The lack of a clear definition for 'explicit consent' may lead to inconsistent interpretations. Add a specific definition.",
      suggested_change: "Add a subsection defining explicit consent as 'a clear affirmative act by which the data subject signifies agreement to the processing of personal data'.",
      citations: [
        {
          id: 2,
          title: "General Data Protection Regulation (GDPR)",
          source: "European Union",
          type: "legal",
          summary: "Regulation on data protection and privacy in the European Union.",
          relevance_score: 0.95
        }
      ],
      confidence: 0.92,
      impact: "high"
    }
  ];

  const [expandedSuggestion, setExpandedSuggestion] = useState(null);

  const toggleSuggestion = (suggestionId) => {
    setExpandedSuggestion(expandedSuggestion === suggestionId ? null : suggestionId);
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high':
        return '#e74c3c';
      case 'medium':
        return '#f39c12';
      case 'low':
        return '#2ecc71';
      default:
        return '#95a5a6';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'objection_response':
        return '⚠️';
      case 'support_acknowledgment':
        return '👍';
      case 'balanced_review':
        return '⚖️';
      default:
        return '📝';
    }
  };

  return (
    <div className="amendment-container">
      <h3>Policy Amendment Suggestions</h3>
      <div className="amendment-description">
        <p>Data-backed recommendations for improving the policy based on public feedback and legal precedents.</p>
      </div>
      
      <div className="suggestion-list">
        {sampleSuggestions.map(suggestion => (
          <div 
            key={suggestion.id} 
            className={`suggestion-card ${expandedSuggestion === suggestion.id ? 'expanded' : ''}`}
          >
            <div 
              className="suggestion-header" 
              onClick={() => toggleSuggestion(suggestion.id)}
            >
              <div className="header-icon">
                {getTypeIcon(suggestion.type)}
              </div>
              <div className="header-content">
                <h4>{suggestion.clause}: {suggestion.summary}</h4>
                <div className="header-meta">
                  <span 
                    className="impact-badge"
                    style={{ backgroundColor: getImpactColor(suggestion.impact) }}
                  >
                    {suggestion.impact} impact
                  </span>
                  <span className="confidence">Confidence: {(suggestion.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="header-toggle">
                {expandedSuggestion === suggestion.id ? '▲' : '▼'}
              </div>
            </div>
            
            {expandedSuggestion === suggestion.id && (
              <div className="suggestion-content">
                <div className="content-section">
                  <h5>Details</h5>
                  <p>{suggestion.details}</p>
                </div>
                
                <div className="content-section">
                  <h5>Suggested Amendment</h5>
                  <div className="amendment-text">
                    {suggestion.suggested_change}
                  </div>
                </div>
                
                <div className="content-section">
                  <h5>Supporting Citations</h5>
                  <div className="citation-list">
                    {suggestion.citations.map(citation => (
                      <div key={citation.id} className="citation-item">
                        <div className="citation-title">{citation.title}</div>
                        <div className="citation-source">{citation.source}</div>
                        <div className="citation-score">
                          Relevance: {(citation.relevance_score * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="content-actions">
                  <button className="btn-primary">Accept Suggestion</button>
                  <button className="btn-secondary">Modify Suggestion</button>
                  <button className="btn-tertiary">Reject Suggestion</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AmendmentSuggestion;