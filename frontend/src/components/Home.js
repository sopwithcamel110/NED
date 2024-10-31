import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
//import { TextField, IconButton, Button } from '@mui/material';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import DeleteIcon from '@mui/icons-material/Delete';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PlusIcon from '@mui/icons-material/Add'; // Customize or import if you have a specific plus icon
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import EmojiSymbolsIcon from '@mui/icons-material/EmojiSymbols';
import NotInterestedIcon from '@mui/icons-material/NotInterested';
import CodeIcon from '@mui/icons-material/Code';
import { TextField, IconButton, Button, Toolbar, Typography } from '@mui/material';
import './Home.css';

const Home = () => {
    const [topics, setTopics] = useState([{ topic: '', textSegments: [''] }]);
    const navigate = useNavigate();

    const handleTopicChange = (index, value) => {
        const newTopics = [...topics];
        newTopics[index].topic = value;
        setTopics(newTopics);
    };

    const handleTextChange = (topicIndex, textIndex, value) => {
        const newTopics = [...topics];
        newTopics[topicIndex].textSegments[textIndex] = value;
        setTopics(newTopics);
    };

    const addTextBox = (topicIndex) => {
        const newTopics = [...topics];
        newTopics[topicIndex].textSegments.push('');
        setTopics(newTopics);
    };

    const removeTextBox = (topicIndex, textIndex) => {
        const newTopics = [...topics];
        newTopics[topicIndex].textSegments.splice(textIndex, 1);
        setTopics(newTopics);
    };

    const deleteTopic = (topicIndex) => {
        const newTopics = topics.filter((_, index) => index !== topicIndex);
        setTopics(newTopics);
    };

    const addNewTopic = () => {
        setTopics([...topics, { topic: '', textSegments: [''] }]);
    };

    const handleNext = () => {
        const allValid = topics.every(topic => topic.topic.trim() !== '' && topic.textSegments.some(segment => segment.trim() !== ''));
        
        if (!allValid) {
            alert('Please ensure all topics have titles and at least one text segment.');
            return;
        }
        navigate('/preview', { state: { topics } });
    };

    return (
        <div className="home-container">
            {/* Welcome Section */}
            <div className="welcome-section">
                <h1>Welcome to Note Sheet Editor</h1>
                <ArrowDownwardIcon className="arrow-icon" />
                <p>Get Started</p>
            </div>

            {/* Main Content Section */}
            <div className="content-section">
                <h2>Enter Notes Here</h2>
                <DragDropContext>
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
                                                    />
                                                    <Toolbar className="toolbar">
                                                        <IconButton><FormatListNumberedIcon /></IconButton>
                                                        <IconButton><FormatListBulletedIcon /></IconButton>
                                                        <IconButton><EmojiSymbolsIcon /></IconButton>
                                                        <IconButton><NotInterestedIcon /></IconButton>
                                                        <IconButton><CodeIcon /></IconButton>
                                                    </Toolbar>
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
                                                                onChange={(e) =>
                                                                    handleTextChange(topicIndex, textIndex, e.target.value)
                                                                }
                                                                className="consistent-textarea"
                                                            />
                                                            <IconButton aria-label="delete" size="medium" onClick={() => removeTextBox(topicIndex, textIndex)}>
                                                                <DeleteIcon fontSize="inherit" />
                                                            </IconButton>
                                                        </div>
                                                    ))}
                                                </div>
                                                <div className="button-row">
                                                    <IconButton onClick={() => addTextBox(topicIndex)} aria-label="add" >
                                                        <PlusIcon />
                                                    </IconButton>
                                                    <Button variant="outlined" color="error" onClick={() => deleteTopic(topicIndex)}>
                                                        Delete Block
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
                    {/* <IconButton onClick={addNewTopic} aria-label="add">
                        <AddCircleOutlineIcon fontSize="large" />
                    </IconButton> */}
                    <Button variant="outlined" color="right" onClick={addNewTopic}>
                        Add Block
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
