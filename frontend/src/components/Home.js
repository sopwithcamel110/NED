import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const [topic, setTopic] = useState('');
  const [textSegments, setTextSegments] = useState(['']);

  const navigate = useNavigate();

  const handleTextChange = (index, value) => {
    const newTextSegments = [...textSegments];
    newTextSegments[index] = value;
    setTextSegments(newTextSegments);
  };

  const addTextBox = () => {
    setTextSegments([...textSegments, '']);
  };

  const removeTextBox = (index) => {
    if (textSegments.length > 1) {
      const newTextSegments = textSegments.filter((_, i) => i !== index);
      setTextSegments(newTextSegments);
    }
  };

  const handleNext = () => {
    const combinedText = textSegments.join(' ').trim();
    navigate('/preview', { state: { text: combinedText, topic } });
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '5%' }}>
      <h1>Enter Your Topic and Text</h1>
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter Topic"
        style={{ width: '60%', marginBottom: '20px' }}
      />
      <div style={{ width: '60%', margin: 'auto', border: '2px solid black', padding: '20px' }}>
        {textSegments.map((segment, index) => (
          <div key={index} style={{ marginBottom: '10px' }}>
            <textarea
              value={segment}
              onChange={(e) => handleTextChange(index, e.target.value)}
              style={{ width: '100%', height: '100px' }}
              placeholder={`Text Box ${index + 1}`}
            />
            <button onClick={() => removeTextBox(index)} style={{ marginTop: '5px' }}>
              Delete
            </button>
          </div>
        ))}
        <button onClick={addTextBox} style={{ marginTop: '10px' }}>
          Add Text Box
        </button>
      </div>
      <button onClick={handleNext} style={{ marginTop: '20px' }}>
        Next
      </button>
    </div>
  );
};

export default Home;