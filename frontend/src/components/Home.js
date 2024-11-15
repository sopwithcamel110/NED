import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PlusIcon from '@mui/icons-material/Add';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import EmojiSymbolsIcon from '@mui/icons-material/EmojiSymbols';
import NotInterestedIcon from '@mui/icons-material/NotInterested';
import CodeIcon from '@mui/icons-material/Code';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { TextField, IconButton, Button, Toolbar, Tooltip } from '@mui/material';
import { Menu, MenuItem } from '@mui/material';
import Grid from '@mui/material/Grid2';
import './Home.css';

const API_BASE_URL = "http://localhost:5000"; // Replace with your actual backend URL

const Home = () => {
    const [topics, setTopics] = useState([]);
    const [anchorEl, setAnchorEl] = useState(null); // For symbol menu
    const contentRef = useRef(null);
    const navigate = useNavigate();

    const updateTopics = (newTopics) => {
        setTopics(newTopics);
    };

    // Save a new topic to the backend
    const saveTopics = async (newTopics) => {
        try {
          const response = await fetch(API_BASE_URL + "/createpdf", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(newTopics),
          });
      
          if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
          }
          console.log("Topics saved successfully");
        } catch (error) {
          console.error("Error saving topics:", error);
        }
      };
      
      const collectAndSaveTopics = () => {
        const topicData = topics.map((topicObj) => ({
          topic: topicObj.topic,
          textSegments: topicObj.textSegments
        }));
      
        saveTopics(topicData);
      };

    // Delete a topic from the backend
    const deleteTopic = async (topicId) => {
        try {
            await fetch(`${API_BASE_URL}/${topicId}`, { method: 'DELETE' });
            console.log("Topic deleted successfully");
        } catch (error) {
            console.error("Error deleting topic:", error);
        }
    };

    const handleTopicChange = (index, value) => {
        const newTopics = [...topics];
        newTopics[index].topic = value;
        updateTopics(newTopics);
    };

    const handleTextChange = (topicIndex, textIndex, value) => {
        const newTopics = [...topics];
        newTopics[topicIndex].textSegments[textIndex] = value;
        updateTopics(newTopics);
    };

    const addNewTopic = () => {
        const newTopic = { topic: '', textSegments: [''] };
        saveTopic(newTopic);
    };

    const onDragEnd = (result) => {
        const { source, destination } = result;
        if (!destination) return;
        const reorderedTopics = Array.from(topics);
        const [movedTopic] = reorderedTopics.splice(source.index, 1);
        reorderedTopics.splice(destination.index, 0, movedTopic);
        updateTopics(reorderedTopics);
    };

    const handleNext = () => {
        // Make sure topics are valid before saving
        const allValid = topics.every(
          (topic) => topic.topic.trim() !== '' && topic.textSegments.some((segment) => segment.trim() !== '')
        );
        
        if (!allValid) {
          alert('Please ensure all topics have titles and at least one text segment.');
          return;
        }
      
        collectAndSaveTopics();
        navigate('/preview', { state: { topics } });
      };

    const scrollToContent = async() => {
        document.getElementById('content-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
        const response = await fetch(API_BASE_URL + "/ping", {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        });
        console.log(response)
    };

    const applyFormatting = (type, topicIndex, textIndex) => {
        const updatedTopics = [...topics];
        let text = updatedTopics[topicIndex].textSegments[textIndex];

        if (type === 'numbered') {
            text = text.split('\n').map((line, i) => `${i + 1}. ${line}`).join('\n');
        } else if (type === 'bulleted') {
            text = text.split('\n').map(line => `• ${line}`).join('\n');
        } else if (type === 'code') {
            text = `\`\`\`\n${text}\n\`\`\``;
        }

        updatedTopics[topicIndex].textSegments[textIndex] = text;
        updateTopics(updatedTopics);
    };

    const symbols = ['★', '✔', '♛', '♪', '☀', '♥', '☺', '✈'];
    const handleSymbolClick = (event) => setAnchorEl(event.currentTarget);
    const handleSymbolSelect = (symbol, topicIndex, textIndex) => {
        const updatedTopics = [...topics];
        const currentText = updatedTopics[topicIndex].textSegments[textIndex];
        updatedTopics[topicIndex].textSegments[textIndex] = currentText + symbol;
        setTopics(updatedTopics);
        setAnchorEl(null);
    };

    return (
        <div className="home-container" >
            {/* Welcome Section */}
            <div className="welcome-section">
                {/* <h1>Welcome to Note Sheet Editor</h1> */}
                {/* testing something out here */}
                <h1> </h1>
                <h1> </h1>
                <h1> </h1>
                <ArrowDownwardIcon className="arrow-icon" onClick={scrollToContent} />
                <p>Get Started</p>
        </div>
        {/* Main Content Section */}
        <div id="content-section" className="content-section">
            <h2>Enter Notes Here</h2>
            <DragDropContext onDragEnd={onDragEnd}>
                <Droppable droppableId="droppable" direction="vertical">
                    {(provided) => (
                        <div ref={provided.innerRef} {...provided.droppableProps}>
                            {topics.map((topicObj, topicIndex) => (
                                <Draggable key={topicIndex} draggableId={`topic-${topicIndex}`} index={topicIndex}>
                                    {(provided) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            className="topic-container"
                                        >
                                            <div className="topic-row">
                                                <TextField
                                                    id="outlined-basic"
                                                    label="Enter Topic"
                                                    variant="outlined"
                                                    value={topicObj.topic}
                                                    onChange={(e) => handleTopicChange(topicIndex, e.target.value)}
                                                    className="topic-input"
                                                    style={{ width: '500px' }}
                                                />
                                                <Toolbar className="toolbar">
                                                    <Tooltip title="Bullet List" arrow>
                                                        <IconButton onClick={() => applyFormatting('bulleted', topicIndex, textIndex)}>
                                                            <FormatListBulletedIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Numbered List" arrow>
                                                        <IconButton onClick={() => applyFormatting('numbered', topicIndex, textIndex)}>
                                                            <FormatListNumberedIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Code Block" arrow>
                                                        <IconButton onClick={() => applyFormatting('code', topicIndex, textIndex)}>
                                                            <CodeIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="No Text Wrap" arrow>
                                                        <IconButton>
                                                            <NotInterestedIcon />
                                                        </IconButton>
                                                    </Tooltip>

                                                    <IconButton onClick={handleSymbolClick}><EmojiSymbolsIcon /></IconButton>
                                                        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
                                                            <Grid container spacing={1} style={{ maxHeight: '200px', overflow: 'auto' }}>
                                                                {symbols.map((symbol, index) => (
                                                                    <Grid item xs={3} key={index}>
                                                                        <MenuItem onClick={() => handleSymbolSelect(symbol, topicIndex, topicIndex)}>{symbol}</MenuItem>
                                                                    </Grid>
                                                                ))}
                                                            </Grid>
                                                        </Menu>
                                                </Toolbar>
                                                <Button
                                                    component="label"
                                                    variant="contained"
                                                    startIcon={<CloudUploadIcon />}
                                                >
                                                    Upload Images
                                                <input
                                                    type="file"
                                                    multiple
                                                    onChange={(event) => console.log(event.target.files)}
                                                    style={{ display: 'none' }}
                                                />
                                                </Button>
                                            </div>

                                            <div className="text-box-container">
                                                {topicObj.textSegments.map((segment, textIndex) => (
                                                    <div key={textIndex} className="text-box">
                                                        <TextField
                                                            id="outlined-multiline-static"
                                                            label="Enter Text"
                                                            multiline
                                                            rows={12}
                                                            value={segment}
                                                            style={{ paddingBottom: '2px' }}
                                                            onChange={(e) =>
                                                                handleTextChange(topicIndex, textIndex, e.target.value)
                                                            }
                                                            className="consistent-textarea"
                                                        />
                                                    </div>
                                                ))}
                                            </div>
                                            <div className="button-row" style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                                <Button 
                                                    variant="outlined" 
                                                    color="error"
                                                    onMouseEnter={(e) => {
                                                        e.target.style.backgroundColor = 'red';
                                                        e.target.style.borderColor = 'black';
                                                        e.target.style.color = 'white';
                                                    }}
                                                    onMouseLeave={(e) => {
                                                        e.target.style.backgroundColor = 'transparent';
                                                        e.target.style.color = 'red';
                                                        e.target.style.borderColor = 'red';
                                                    }}
                                                    onClick={() => deleteTopic(topicIndex)}
                                                >
                                                    <DeleteIcon/> Delete Block
                                                </Button>
                                            </div>

                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>

            <div className="footer-buttons2">
                <Button 
                    variant="outlined"
                    onClick={addNewTopic} 
                    style={{
                        border: '1px solid #333',
                        padding: '20px 20px',
                        fontSize: '2rem',
                        minWidth: '50px',
                        transition: 'background-color 0.3s ease',
                        backgroundColor: 'white',
                        color: 'black'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.backgroundColor = 'lightgray';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.backgroundColor = 'white';
                    }}
                >
                    <PlusIcon style={{ backgroundColor: 'transparent' }} />
                </Button>
            </div>


            <div className="footer-buttons">
                <IconButton onClick={handleNext} aria-label="next">
                    <ArrowForwardIcon fontSize="large" />
                </IconButton>
            </div>
        </div>
    </div>
    );
};

export default Home;
