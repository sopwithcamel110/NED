import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
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

    const onDragEnd = (result) => {
        if (!result.destination) return;

        const reorderedTopics = Array.from(topics);
        const [moved] = reorderedTopics.splice(result.source.index, 1);
        reorderedTopics.splice(result.destination.index, 0, moved);
        setTopics(reorderedTopics);
    };

    return (
        <div className="container">
            <h1>Enter Your Topics and Texts</h1>
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
                                            <input
                                                type="text"
                                                value={topicObj.topic}
                                                onChange={(e) => handleTopicChange(topicIndex, e.target.value)}
                                                placeholder={`Enter Topic ${topicIndex + 1}`}
                                                className="topic-input"
                                            />
                                            <div className="text-box-container">
                                                {topicObj.textSegments.map((segment, textIndex) => (
                                                    <div key={textIndex} className="text-box">
                                                        <textarea
                                                            value={segment}
                                                            onChange={(e) =>
                                                                handleTextChange(topicIndex, textIndex, e.target.value)
                                                            }
                                                            placeholder={`Text Box ${textIndex + 1}`}
                                                            className="consistent-textarea"
                                                        />
                                                        <button
                                                            className="delete-btn"
                                                            onClick={() => removeTextBox(topicIndex, textIndex)}
                                                        >
                                                            Delete Text Box
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                            <button
                                                className="add-textbox-button"
                                                onClick={() => addTextBox(topicIndex)}
                                            >
                                                Add Text Box
                                            </button>
                                            <button className="delete-topic-btn" onClick={() => deleteTopic(topicIndex)}>
                                                Delete Topic
                                            </button>
                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>
            <button className="new-topic-button" onClick={addNewTopic}>
                Add New Topic
            </button>
            <button className="next-button" onClick={handleNext}>
                Next
            </button>
        </div>
    );
};

export default Home;