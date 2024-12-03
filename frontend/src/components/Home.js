import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import SuperscriptIcon from '@mui/icons-material/Superscript';
import SubscriptIcon from '@mui/icons-material/Subscript';
import CodeIcon from '@mui/icons-material/Code';
import { TextField, IconButton, Divider, Button, Toolbar, Tooltip, Menu, MenuItem, FormControlLabel, Checkbox } from '@mui/material';
import FunctionsIcon from '@mui/icons-material/Functions';
import Grid from '@mui/material/Grid2';
import './Home.css';

const API_BASE_URL = "http://localhost:5000"; // Replace with your actual backend URL

const Home = () => {
    const [topics, setTopics] = useState(() => {
        const savedTopics = JSON.parse(localStorage.getItem('topics'));

        return Array.isArray(savedTopics) && savedTopics.length > 0 ? savedTopics : [{ topic: '', textSegments: [''], media: 'text', nowrap: false }];
    });
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Log whenever `isLoading` changes for debugging
        console.log('isLoading changed:', isLoading);
    }, [isLoading]);

    //states for math symbol menu, selected topic and text
    const [symbolMenuAnchorEl, setSymbolMenuAnchorEl] = useState(null); 
    const [selectedTopicIndex, setSelectedTopicIndex] = useState(null);
    const [selectedTextIndex, setSelectedTextIndex] = useState(null); 

    //functionality for nowrap toggle button
    const handleNoWrapChange = (index) => {
        const newTopics = [...topics];
        newTopics[index].nowrap = !newTopics[index].nowrap;
        updateTopics(newTopics);
    };

    const [maxPages, setMaxPages] = useState(null); // state for "Max pages"

    const handleMaxPagesChange = (event) => { //function for 'max pages' integer to never go below 0
        let value = event.target.value;
        if (value <= 0){
            value = "";
        }
        setMaxPages(value === "" ? null : parseInt(value));
    };
    
    const updateTopics = (newTopics) => {
        setTopics(newTopics);
    };

    // Save a new topic to the backend
    const saveTopics = async (formData) => {
        var response = await fetch(API_BASE_URL + "/createpdf", {
            method: "POST",
            body: formData,
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob); // Convert Blob to an Object URL
            return url;
        } else {
            console.error("Failed to generate PDF");
            return "";
        }
      };

    // collects topics data and send to backend
    const collectAndSaveTopics = async () => {
        const formData = new FormData();

        formData.append(`meta_max_pages`, maxPages);
        topics.forEach((topic, index) => {
            if (topic.file) {
                formData.append(`file_${index}`, topic.file);
            } else {
                formData.append(`data_${index}`, JSON.stringify({
                    'topic': topic.topic,
                    'content': topic.textSegments[0].trim().split('\n'),
                    'media': topic.media,
                    'nowrap': topic.nowrap,
                  }));
            }
        });
        return await saveTopics(formData);
    };

    // Delete a topic from the backend
    const deleteTopic = async (index) => {
        setTopics((prevTopics) => {
            // Create a new array without the topic at the given index
            const updatedTopics = prevTopics.filter((_, i) => i !== index);
            // Save the updated array to localStorage
            localStorage.setItem('topics', JSON.stringify(updatedTopics));
            // Return the updated array to update state
            return updatedTopics;
        });
    };

    
    const handleTopicChange = (index, value) => { //topic change
        const newTopics = [...topics];
        newTopics[index].topic = value;
        updateTopics(newTopics);
    };

    const handleTextChange = (topicIndex, textIndex, value) => { //text change
        const newTopics = [...topics];
        newTopics[topicIndex].textSegments[textIndex] = value;
        updateTopics(newTopics);
    };

    const addTextTopic = () => { //create new topic/content box
        const newTopic = { topic: '', textSegments: [''], media: 'text', nowrap: false };
        setTopics([...topics, newTopic]);
    };

    const addImageTopic = (event) => { //create new image box
        const file = event.target.files[0];
        const newTopic = { url: URL.createObjectURL(file), file, media: 'image' };
        setTopics([...topics, newTopic]);
    };

    const onDragEnd = (result) => { //drag and drop topic/content box
        const { source, destination } = result;
        if (!destination) return;
        const reorderedTopics = Array.from(topics);
        const [movedTopic] = reorderedTopics.splice(source.index, 1);
        reorderedTopics.splice(destination.index, 0, movedTopic);
        updateTopics(reorderedTopics);
    };

    const handleNext = async () => { //handles what occurs when 'next' button is clicked. Error handling
        setIsLoading(true);
        const allValid = topics?.filter((t) => t.media === 'text').every(
          (topic) =>
            topic.topic.trim() !== '' &&
            topic.textSegments.some((segment) => segment.trim() !== '')
        );
        if (!allValid) {
          showErrorToast('Please ensure all topics have titles and at least one text segment.', 'red');
          setIsLoading(false);
          return;
        }
      
        try {
          localStorage.setItem('topics', JSON.stringify(topics));
          const location = await collectAndSaveTopics();
          if (!location) {
            showErrorToast('Failed to generate preview.', 'orange');
            setIsLoading(false);
            return;
          }
          navigate('/preview', { state: { pdfLocation: location } });
        } catch (error) {
          showErrorToast('An error occurred while processing your request.', 'red');
          console.error(error);
        }
        setIsLoading(false);
    };
      
    function showErrorToast(errMsg, backgroundColor = 'black') { //function to show error. called from "handleNext" function
        let container = document.getElementById('toast-container');
        if (!container) {
          container = document.createElement('div');
          container.id = 'toast-container';
          document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.classList.add('toast');
        toast.textContent = errMsg;
        toast.style.backgroundColor = backgroundColor;
        toast.style.color = 'white';
        toast.style.padding = '10px';
        toast.style.margin = '10px 0';
        toast.style.borderRadius = '5px';
        toast.style.position = 'relative';
        toast.style.animation = 'fade-in-out 3s forwards';
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }   

    const scrollToContent = async() => { //called when button on landing page is clicked. Brings user to text input area
        document.getElementById('content-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
        try {
            await fetch(API_BASE_URL + "/ping", {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });
        }
        catch {
            console.log("API IS NOT RUNNING. RUN THE API IN THE BACKEND FOLDER BEFORE STARTING THIS APPLICATION.")
        }
    };

    //bulletpoint, numlist application to content area of specified topic/content box
    const applyFormatting = (type, topicIndex, textIndex) => {
        const updatedTopics = [...topics];
        const text = updatedTopics[topicIndex].textSegments[textIndex];
        const removeFormatting = (lines) => 
            lines.map(line => line.replace(/^•\s|^\d+\.\s/, ''));
        const lines = text.split('\n');
        const strippedLines = removeFormatting(lines);
        if (type === 'numbered') {
            updatedTopics[topicIndex].textSegments[textIndex] = strippedLines
                .map((line, i) => `${i + 1}. ${line}`)
                .join('\n');
        } else if (type === 'bulleted') {
            updatedTopics[topicIndex].textSegments[textIndex] = strippedLines
                .map((line) => `• ${line}`)
                .join('\n');
        }
        updateTopics(updatedTopics);
    };

    //inserts symbols, exponent or subscript where cursor is located at in textbox
    const insertAtCursor = (topicIndex, textIndex, insertText) => {
        const updatedTopics = [...topics];
        const textFieldId = `text-segment-${topicIndex}-${textIndex}`;
        const textField = document.getElementById(textFieldId);
    
        if (textField) {
            const { selectionStart, selectionEnd } = textField;
            const currentText = updatedTopics[topicIndex].textSegments[textIndex];
            updatedTopics[topicIndex].textSegments[textIndex] = 
                currentText.slice(0, selectionStart) + 
                insertText + 
                currentText.slice(selectionEnd);
            updateTopics(updatedTopics);
            setTimeout(() => {
                textField.selectionStart = textField.selectionEnd = selectionStart + insertText.length;
                textField.focus();
            }, 0);
        }
    };

    const insertExponent = (topicIndex, textIndex) => {
        insertAtCursor(topicIndex, textIndex, "^{}");
    };

    const insertSubscript = (topicIndex, textIndex) => {
        insertAtCursor(topicIndex, textIndex, "_{}");
    };

    const insertSymbol = (topicIndex, textIndex, symbol) => {
        insertAtCursor(topicIndex, textIndex, symbol)
    }
    
    const insertCodeBlock = (topicIndex, textIndex) => {  //unfinished. Ideally denotes content that should be considered "code"
        const updatedTopics = [...topics];
        const currentText = updatedTopics[topicIndex].textSegments[textIndex];
        updatedTopics[topicIndex].textSegments[textIndex] = currentText + '<<< >>>';
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

    return (
        <div className="home-container" >
            {/* Welcome Section */}
            <div className="welcome-section">
                <div className="icon"></div>
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        background: 'rgba(255, 255, 255, 0.5)',
                        backdropFilter: 'blur(10px)',
                        height: '300px',
                        width: '800px',
                        border: '1px solid gray',
                        borderRadius: '8px',
                        cursor: 'pointer',
                    }}
                    >
                    <h1>Welcome to Note Sheet Editor</h1>
                    <ArrowDownwardIcon className="arrow-icon" onClick={scrollToContent} />
                    <p>Click to Start</p>
                </div>
            </div>
            {/* Main Content Section */}
            <div id="content-section" className="content-section">
                <TextField
                    id="max-pages-input"
                    label="Max Pages"
                    type="number"
                    variant="outlined"
                    value={maxPages !== null ? maxPages : ""}
                    onChange={handleMaxPagesChange}
                    style={{ marginBottom: '20px', width: '200px' }}
                    helperText="Optional. Defaults to infinite."
                />
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
                                            {topicObj.media == 'text' ? <><div className="topic-row">
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
                                                        <IconButton onClick={() => applyFormatting('bulleted', topicIndex, 0)}>
                                                            <FormatListBulletedIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Numbered List" arrow>
                                                        <IconButton onClick={() => applyFormatting('numbered', topicIndex, 0)}>
                                                            <FormatListNumberedIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Tooltip title="Code Block" arrow>
                                                        <IconButton onClick={() => insertCodeBlock(topicIndex, 0)}>
                                                            <CodeIcon />
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
                                                    <Tooltip title="Insert Symbol" arrow>
                                                        <IconButton onClick={(e) => handleSymbolMenuOpen(e, topicIndex, 0)}>
                                                            <FunctionsIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                    <Divider 
                                                        orientation="vertical" 
                                                        flexItem 
                                                        sx={{ margin: '0 10px' }}
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={topicObj.nowrap}
                                                                onChange={(e) => handleNoWrapChange(topicIndex)}
                                                                color="primary"
                                                            />
                                                        }
                                                        label="No Text Wrap"
                                                    />
                                                </Toolbar>
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
                                            </div></>:<><img
                                    key={topicIndex}
                                    src={topicObj.url}
                                    alt={`Uploaded ${topicIndex + 1}`}
                                    style={{ width: '100px', margin: '10px' }}
                                /></>}

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
                                                    <DeleteIcon/>
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
                        '∞', 'π', 'e', 'Σ', 'Ω', 'Δ', '∑', '±', '∩', '√',
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
                                    onClick={function() {
                                        insertSymbol(selectedTopicIndex, selectedTextIndex, symbol);
                                        handleSymbolMenuClose();
                                    }}
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
                <Button variant="contained" component="span" onClick={addTextTopic}>
                    Add Text
                </Button>
                <label htmlFor="image-upload">
                <input
                    accept="image/*"
                    id="image-upload"
                    type="file"
                    style={{ display: 'none' }}
                    onChange={addImageTopic}
                />
                <Button variant="contained" component="span">
                    Add Image
                </Button>
                </label>
            </div>

            {isLoading ? (
                        <div className="spinner-overlay">
                            <img 
                                src="https://media1.tenor.com/m/N5NKR5L3choAAAAd/writing-eric-cartman.gif" 
                                alt="Loading..." 
                                className="spinner-gif" 
                            />
                            <div className="spinner-text">Generating...</div>
                        </div>
                    ) : (
                        <div className="footer-buttons">
                            <IconButton onClick={handleNext} aria-label="next">
                                <ArrowForwardIcon fontSize="large" />
                            </IconButton>
                        </div>
                    )}
            </div>
        </div>
    );
};

export default Home;
