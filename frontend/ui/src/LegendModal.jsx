import React from 'react';

/**
 * LegendModal - Reusable modal component for displaying FIX protocol legends
 * 
 * Props:
 * - isOpen: Boolean indicating if modal should be displayed
 * - onClose: Callback function to close the modal
 * - title: Title of the legend
 * - description: Description text to display below title
 * - legendData: Object with codes as keys and { title, description } as values
 */
export default function LegendModal({ isOpen, onClose, title, description, legendData }) {
  if (!isOpen) return null;

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <p>{description}</p>
        <div className="status-legend-grid">
          {Object.entries(legendData).map(([code, info]) => (
            <div key={code} className="status-legend-item">
              <span className={`status-chip ${info.className || ''}`}>{code}</span>
              <div>
                <strong>{info.title}</strong>
                <p>{info.description}</p>
              </div>
            </div>
          ))}
        </div>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
