import React, { useState, useRef} from 'react';
import { useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PlusIcon from '@mui/icons-material/Add';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import SuperscriptIcon from '@mui/icons-material/Superscript';
import SubscriptIcon from '@mui/icons-material/Subscript';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
// import EmojiSymbolsIcon from '@mui/icons-material/EmojiSymbols';
import NotInterestedIcon from '@mui/icons-material/NotInterested';
import CodeIcon from '@mui/icons-material/Code';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { TextField, IconButton, Button, Toolbar, Tooltip, Menu, MenuItem } from '@mui/material';
import FunctionsIcon from '@mui/icons-material/Functions';
import Grid from '@mui/material/Grid2';
import './Home.css';

const Home = () => {
    const [topics, setTopics] = useState(() => {
        const savedTopics = localStorage.getItem('topics');
        return savedTopics ? JSON.parse(savedTopics) : [{ topic: '', textSegments: [''] }];
    });
    const navigate = useNavigate();

    //math symbols
    const [symbolMenuAnchorEl, setSymbolMenuAnchorEl] = useState(null); 
    const [selectedTopicIndex, setSelectedTopicIndex] = useState(null);
    const [selectedTextIndex, setSelectedTextIndex] = useState(null); 

    const updateTopics = (newTopics) => {
        setTopics(newTopics);
        localStorage.setItem('topics', JSON.stringify(newTopics));
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

    const deleteTopic = (topicIndex) => {
        const newTopics = topics.filter((_, index) => index !== topicIndex);
        updateTopics(newTopics);
    };

    const addNewTopic = () => {
        updateTopics([...topics, { topic: '', textSegments: [''] }]);
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
        const allValid = topics.every(topic => topic.topic.trim() !== '' && topic.textSegments.some(segment => segment.trim() !== ''));
        if (!allValid) {
            alert('Please ensure all topics have titles and at least one text segment.');
            return;
        }
        navigate('/preview', { state: { topics } });
    };

    const scrollToContent = () => {
        document.getElementById('content-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    
    const insertExponent = (topicIndex, textIndex) => { //exponent button
        const updatedTopics = [...topics];
        const currentText = updatedTopics[topicIndex].textSegments[textIndex];
        updatedTopics[topicIndex].textSegments[textIndex] = currentText + '^{}';
        updateTopics(updatedTopics);
    };


    const insertSubscript = (topicIndex, textIndex) => {  //subscript Button
        const updatedTopics = [...topics];
        const currentText = updatedTopics[topicIndex].textSegments[textIndex];
        updatedTopics[topicIndex].textSegments[textIndex] = currentText + '_{}';
        updateTopics(updatedTopics);
    };

    const insertFraction = (topicIndex, textIndex) => {  //Fraction
        const updatedTopics = [...topics];
        const currentText = updatedTopics[topicIndex].textSegments[textIndex];
        updatedTopics[topicIndex].textSegments[textIndex] = currentText + '{}/{}';
        updateTopics(updatedTopics);
    };

    const insertSQRT = (topicIndex, textIndex) => {  //Square root bttn
        const updatedTopics = [...topics];
        const currentText = updatedTopics[topicIndex].textSegments[textIndex];
        updatedTopics[topicIndex].textSegments[textIndex] = currentText + '√{}';
        updateTopics(updatedTopics);
    };

    //math symbol dropdown menu
    const handleSymbolMenuOpen = (event, topicIndex, textIndex) => {
        setSymbolMenuAnchorEl(event.currentTarget);
        setSelectedTopicIndex(topicIndex);
        setSelectedTextIndex(textIndex);
    };
    
    const handleSymbolMenuClose = () => {
        setSymbolMenuAnchorEl(null);
    };
    
    const handleSymbolSelect = (symbol) => {
        const updatedTopics = [...topics];
        const currentText = updatedTopics[selectedTopicIndex].textSegments[selectedTextIndex];
        updatedTopics[selectedTopicIndex].textSegments[selectedTextIndex] = currentText + symbol;
        updateTopics(updatedTopics);
        handleSymbolMenuClose();
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
                                                    <Tooltip title="Exponent" arrow>
                                                        <IconButton onClick={() => insertExponent(topicIndex, 0)}>
                                                            <SuperscriptIcon/>
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Subscript" arrow>
                                                        <IconButton onClick={() => insertSubscript(topicIndex, 0)}>
                                                            <SubscriptIcon/>
                                                        </IconButton>
                                                    </Tooltip>

                                                    <Tooltip title="Fraction" arrow>
                                                        <IconButton onClick={() => insertFraction(topicIndex, 0)}>
                                                            <QuestionMarkIcon/>
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Square Root" arrow>
                                                        <IconButton onClick={() => insertSQRT(topicIndex, 0)}>
                                                            <QuestionMarkIcon/>
                                                        </IconButton>
                                                    </Tooltip>

                                                    <Tooltip title="Insert Symbol" arrow>
                                                        <IconButton onClick={(e) => handleSymbolMenuOpen(e, topicIndex, 0)}>
                                                            <FunctionsIcon />
                                                        </IconButton>
                                                    </Tooltip>
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
                                                        id={`text-segment-${topicIndex}-${textIndex}`}
                                                        label="Enter Text"
                                                        multiline
                                                        rows={12}
                                                        value={segment}
                                                        style={{ paddingBottom: '2px' }}
                                                        onChange={(e) => handleTextChange(topicIndex, textIndex, e.target.value)}
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
                
            <Menu
                anchorEl={symbolMenuAnchorEl}
                open={Boolean(symbolMenuAnchorEl)}
                onClose={handleSymbolMenuClose}
                PaperProps={{
                    style: {
                        maxHeight: '400px',
                        overflowY: 'auto', 
                        width: '500px',
                    },
                }}
            >
                <Grid
                    container
                    spacing={1}
                    style={{ padding: '10px', display: 'flex', flexWrap: 'wrap' }}
                >
                    {[
                        '∞', 'π', 'e', 'Σ', 'Ω', 'Δ', '∑', '√', '±', '∩',
                        '∪', '∈', '∉', '⊂', '⊃', '⊆', '⊇', '∃', '∀', '∧',
                        '∨', '⇒', '⇔', '∇', '∂', '⊥', '⊤', '≠', '≈', '≡',
                        '≪', '≫', '∝', '∼', '≈', '∫', '∮', '∅', '∴', '⊕',
                        '⊗', '⊘', '⊔', '⊓', '∧', '∨', '∼', '⊂', '⊃', '⋅',
                        '⊔', '⊓', 'ℵ', 'ℝ', 'ℕ', 'ℤ', 'ℚ', 'ℂ', 'ℍ', '↔',
                        '←', '→', '∘', 
                    ].map(function(symbol, index) {
                        return (
                            <Grid item xs={2} sm={1} md={1} key={index}>
                                <MenuItem
                                    onClick={function() { handleSymbolSelect(symbol); }}
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'center',
                                        padding: '5px 10px',
                                    }}
                                >
                                    {symbol}
                                </MenuItem>
                            </Grid>
                        );
                    })}
                </Grid>
            </Menu>

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
