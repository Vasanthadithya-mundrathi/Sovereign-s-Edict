import React, { useState } from 'react';
import './CitationPanel.css';

const CitationPanel = ({ data }) => {
  // Sample citation data
  const sampleCitations = [
    {
      id: 1,
      title: "Puttaswamy Judgment on Privacy Rights",
      source: "Supreme Court of India",
      type: "legal",
      summary: "Landmark judgment establishing privacy as a fundamental right under the Indian Constitution.",
      relevance: 0.98,
      url: "https://example.com/puttaswamy-judgment"
    },
    {
      id: 2,
      title: "General Data Protection Regulation (GDPR)",
      source: "European Union",
      type: "legal",
      summary: "Regulation on data protection and privacy in the European Union.",
      relevance: 0.95,
      url: "https://example.com/gdpr"
    },
    {
      id: 3,
      title: "Economic Impact of Data Privacy Laws",
      source: "Journal of Digital Economics",
      type: "academic",
      summary: "Study on the economic effects of implementing strict data privacy regulations.",
      relevance: 0.85,
      url: "https://example.com/economic-impact"
    },
    {
      id: 4,
      title: "Data Breach Notification Requirements",
      source: "International Privacy Review",
      type: "expert",
      summary: "Analysis of notification requirements in data protection laws across jurisdictions.",
      relevance: 0.92,
      url: "https://example.com/breach-notification"
    }
  ];

  const [selectedCitation, setSelectedCitation] = useState(null);

  const getTypeBadge = (type) => {
    const typeConfig = {
      legal: { color: '#e74c3c', label: 'Legal Precedent' },
      academic: { color: '#3498db', label: 'Academic Research' },
      expert: { color: '#2ecc71', label: 'Expert Analysis' }
    };
    
    return typeConfig[type] || { color: '#95a5a6', label: 'Other' };
  };

  return (
    <div className="citation-container">
      <h3>Citation & Reference Panel</h3>
      <div className="citation-description">
        <p>All insights and recommendations are backed by verified sources to ensure accuracy and credibility.</p>
      </div>
      
      <div className="citation-content">
        <div className="citation-list">
          <h4>Relevant Citations</h4>
          {sampleCitations.map(citation => {
            const typeInfo = getTypeBadge(citation.type);
            return (
              <div 
                key={citation.id} 
                className={`citation-item ${selectedCitation?.id === citation.id ? 'selected' : ''}`}
                onClick={() => setSelectedCitation(citation)}
              >
                <div className="citation-header">
                  <h5>{citation.title}</h5>
                  <span 
                    className="citation-type" 
                    style={{ backgroundColor: typeInfo.color }}
                  >
                    {typeInfo.label}
                  </span>
                </div>
                <div className="citation-source">
                  <strong>Source:</strong> {citation.source}
                </div>
                <div className="citation-relevance">
                  <div className="relevance-bar">
                    <div 
                      className="relevance-fill" 
                      style={{ width: `${citation.relevance * 100}%` }}
                    ></div>
                  </div>
                  <span>Relevance: {(citation.relevance * 100).toFixed(0)}%</span>
                </div>
              </div>
            );
          })}
        </div>
        
        {selectedCitation && (
          <div className="citation-details">
            <div className="details-header">
              <h4>{selectedCitation.title}</h4>
              <span 
                className="citation-type-large" 
                style={{ backgroundColor: getTypeBadge(selectedCitation.type).color }}
              >
                {getTypeBadge(selectedCitation.type).label}
              </span>
            </div>
            <div className="details-source">
              <strong>Source:</strong> {selectedCitation.source}
            </div>
            <div className="details-summary">
              <h5>Summary</h5>
              <p>{selectedCitation.summary}</p>
            </div>
            <div className="details-actions">
              <button className="btn-primary">
                <a href={selectedCitation.url} target="_blank" rel="noopener noreferrer">
                  View Full Document
                </a>
              </button>
              <button className="btn-secondary">Cite This Source</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CitationPanel;