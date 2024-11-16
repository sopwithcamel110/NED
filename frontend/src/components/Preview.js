import React from 'react';
import { Button, IconButton } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CompressIcon from '@mui/icons-material/Compress';
import { useNavigate } from 'react-router-dom';

const Preview = () => {
  const navigate = useNavigate();
  const pdfPath = `${process.env.PUBLIC_URL}/sample.pdf`; // Path to the PDF in the public folder

  const handleBack = () => {
    navigate(-1); // Go back to the previous page
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = pdfPath; // Path to the PDF
    link.download = 'sample.pdf'; // Default download name
    link.click();
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
        <Button variant="contained" startIcon={<DownloadIcon />} onClick={handleDownload}>
          Download
        </Button>
      </div>
      <div
        style={{
          width: 'calc(21cm / 1.5)',
          height: 'calc(29.7cm / 1.75)',
          border: '1px solid black',
          margin: 'auto',
          backgroundColor: 'white',
          overflow: 'hidden',
        }}
      >
        <iframe
          src={pdfPath}
          title="PDF Preview"
          style={{ width: '100%', height: '100%', border: 'none' }}
        ></iframe>
      </div>
    </div>
  );
};

export default Preview;
