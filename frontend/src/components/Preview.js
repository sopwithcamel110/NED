import React from 'react';
import { useLocation } from 'react-router-dom';

const Preview = () => {
  const location = useLocation();
  const { text } = location.state || '';

  return (
    <div style={{ textAlign: 'center', marginTop: '5%' }}>
      <h1>Preview of Your Text:</h1>
      <div
        style={{
          width: 'calc(21cm/1.5)',
          height: 'calc(29.7cm/1.75)', // A4 height divided to fit on screen
          border: '1px solid black',
          margin: 'auto',
          padding: '20px',
          backgroundColor: 'white',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          boxSizing: 'border-box',
        }}
      >
        <p style={{ whiteSpace: 'pre-wrap', flexGrow: 1 }}>{text}</p>
      </div>
    </div>
  );
};

export default Preview;