import React from 'react';
import './HeatmapVisualization.css';

const HeatmapVisualization = ({ data }) => {
  // Sample data structure for the heatmap
  const sampleData = [
    { clause: 'Section 1', arguments: 5, sentiment: 'positive' },
    { clause: 'Section 2', arguments: 12, sentiment: 'negative' },
    { clause: 'Section 3', arguments: 8, sentiment: 'neutral' },
    { clause: 'Section 4', arguments: 15, sentiment: 'negative' },
    { clause: 'Section 5', arguments: 3, sentiment: 'positive' },
    { clause: 'Section 6', arguments: 7, sentiment: 'neutral' },
    { clause: 'Section 7(a)', arguments: 22, sentiment: 'negative' },
    { clause: 'Section 7(b)', arguments: 18, sentiment: 'negative' },
    { clause: 'Section 8', arguments: 6, sentiment: 'positive' },
    { clause: 'Section 9', arguments: 9, sentiment: 'neutral' },
    { clause: 'Section 10', arguments: 14, sentiment: 'negative' },
  ];

  // Function to determine color based on sentiment and argument count
  const getColor = (sentiment, count) => {
    const intensity = Math.min(count / 25, 1); // Normalize count to 0-1
    
    switch (sentiment) {
      case 'positive':
        return `rgba(46, 204, 113, ${0.3 + intensity * 0.7})`;
      case 'negative':
        return `rgba(231, 76, 60, ${0.3 + intensity * 0.7})`;
      case 'neutral':
        return `rgba(52, 152, 219, ${0.3 + intensity * 0.7})`;
      default:
        return `rgba(189, 195, 199, ${0.3 + intensity * 0.7})`;
    }
  };

  return (
    <div className="heatmap-container">
      <h3>Clause-Level Argument Density Heatmap</h3>
      <div className="heatmap-legend">
        <div className="legend-item">
          <div className="legend-color positive"></div>
          <span>Support</span>
        </div>
        <div className="legend-item">
          <div className="legend-color negative"></div>
          <span>Objection</span>
        </div>
        <div className="legend-item">
          <div className="legend-color neutral"></div>
          <span>Neutral</span>
        </div>
      </div>
      <div className="heatmap-grid">
        {sampleData.map((item, index) => (
          <div 
            key={index} 
            className="heatmap-cell"
            style={{ 
              backgroundColor: getColor(item.sentiment, item.arguments),
              border: '1px solid #ddd'
            }}
            title={`${item.clause}: ${item.arguments} arguments (${item.sentiment})`}
          >
            <div className="cell-content">
              <div className="clause-label">{item.clause}</div>
              <div className="argument-count">{item.arguments}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="heatmap-description">
        <p>This heatmap shows the density and sentiment of arguments for each policy clause. 
        Red indicates high objection, green indicates strong support, and blue represents neutral feedback.</p>
      </div>
    </div>
  );
};

export default HeatmapVisualization;