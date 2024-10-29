import React from 'react';
import { useLocation } from 'react-router-dom';

const Preview = () => {
  const location = useLocation();
  const { topics } = location.state || { topics: [] };

  return (
    <div style={{ textAlign: 'center', marginTop: '5%' }}>
      <h1>Preview of Your Topics and Texts</h1>
      <div
        style={{
          width: 'calc(21cm / 1.5)',
          height: 'calc(29.7cm / 1.75)',
          border: '1px solid black',
          margin: 'auto',
          padding: '20px',
          backgroundColor: 'white',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          boxSizing: 'border-box',
          overflowY: 'auto',
        }}
      >
        {topics.map((topicObj, index) => (
          <div key={index} style={{ marginBottom: '15px' }}>
            <h2>Topic {index + 1}: {topicObj.topic || 'Untitled'}</h2>
            <div style={{ marginLeft: '10px' }}>
              {topicObj.textSegments.map((segment, idx) => (
                <p key={idx} style={{ whiteSpace: 'pre-wrap', margin: '10px 0' }}>
                  {segment}
                </p>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Preview; // Ensure this line exists