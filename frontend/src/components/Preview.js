import React from 'react';
import { Button, IconButton } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import CompressIcon from '@mui/icons-material/Compress';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate, useLocation } from 'react-router-dom';

const Preview = () => {
  const location = useLocation();
  const { topics } = location.state || { topics: [] };
  const navigate = useNavigate();

  const handleBack = () => {
      navigate(-1);
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '5%' }}>
      <h1>Preview of Your Sheet</h1>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' }}>
                 <IconButton onClick={handleBack} aria-label="back">
                    <ArrowBackIcon fontSize="large" />
                </IconButton>
                <Button variant="outlined" startIcon={<CompressIcon />}>
                    Compress
                </Button>
                <Button variant="contained" startIcon={<DownloadIcon />}>
                    Download
                </Button>
            </div>
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

export default Preview;
