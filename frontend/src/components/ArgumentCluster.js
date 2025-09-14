import React, { useState } from 'react';
import './ArgumentCluster.css';

const ArgumentCluster = ({ data }) => {
  // Sample data for argument clusters
  const sampleClusters = [
    {
      id: 1,
      theme: 'Privacy Concerns',
      count: 24,
      sentiment: 'negative',
      arguments: [
        'Section 7(a) requires notification within 72 hours, but what happens if the breach is discovered after this period?',
        'I worry that Section 7(b) might cause unnecessary panic if every minor breach requires individual notification.',
        "I'm concerned that Section 3 doesn't define what constitutes 'explicit consent'. This could lead to inconsistent interpretations."
      ]
    },
    {
      id: 2,
      theme: 'Economic Impact',
      count: 18,
      sentiment: 'neutral',
      arguments: [
        'The penalties in Section 10 seem appropriate and align with international standards like GDPR.',
        'Implementing these requirements may impose significant costs on small businesses.',
        'The economic benefits of increased privacy protection should be weighed against implementation costs.'
      ]
    },
    {
      id: 3,
      theme: 'Legal Compliance',
      count: 15,
      sentiment: 'positive',
      arguments: [
        'The user rights outlined in Section 5 are comprehensive and should empower individuals to control their data.',
        'The enforcement mechanism in Section 9 is essential for ensuring compliance with the Act.',
        'Section 8\'s restriction on international data transfers may hinder the operations of global tech companies.'
      ]
    },
    {
      id: 4,
      theme: 'Technical Implementation',
      count: 12,
      sentiment: 'neutral',
      arguments: [
        'The data minimization principle in Section 4 is crucial for protecting user privacy.',
        'Organizations will need significant technical resources to implement these requirements.',
        'The technical standards for data security in Section 6 should be more specific.'
      ]
    }
  ];

  const [expandedCluster, setExpandedCluster] = useState(null);

  const toggleCluster = (clusterId) => {
    setExpandedCluster(expandedCluster === clusterId ? null : clusterId);
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '#2ecc71';
      case 'negative':
        return '#e74c3c';
      case 'neutral':
        return '#3498db';
      default:
        return '#95a5a6';
    }
  };

  return (
    <div className="cluster-container">
      <h3>Argument Clusters by Theme</h3>
      <div className="cluster-description">
        <p>Arguments have been grouped by theme to identify common concerns and support areas.</p>
      </div>
      <div className="cluster-list">
        {sampleClusters.map(cluster => (
          <div 
            key={cluster.id} 
            className={`cluster-card ${expandedCluster === cluster.id ? 'expanded' : ''}`}
          >
            <div 
              className="cluster-header" 
              onClick={() => toggleCluster(cluster.id)}
              style={{ borderLeftColor: getSentimentColor(cluster.sentiment) }}
            >
              <div className="cluster-title">
                <h4>{cluster.theme}</h4>
                <span className="cluster-count">{cluster.count} arguments</span>
              </div>
              <div className="cluster-sentiment">
                <span 
                  className="sentiment-badge"
                  style={{ backgroundColor: getSentimentColor(cluster.sentiment) }}
                >
                  {cluster.sentiment}
                </span>
              </div>
              <div className="cluster-toggle">
                {expandedCluster === cluster.id ? '▲' : '▼'}
              </div>
            </div>
            {expandedCluster === cluster.id && (
              <div className="cluster-content">
                <h5>Sample Arguments:</h5>
                <ul>
                  {cluster.arguments.map((arg, index) => (
                    <li key={index}>{arg}</li>
                  ))}
                </ul>
                <div className="cluster-actions">
                  <button className="btn-primary">View All Arguments</button>
                  <button className="btn-secondary">Export Cluster</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ArgumentCluster;