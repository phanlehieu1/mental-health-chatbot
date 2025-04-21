import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message }) => {
    const getInitials = (name) => {
        return name.charAt(0).toUpperCase();
    };

    return (
        <div className={`message ${message.role === 'user' ? 'user-message' : 'bot-message'}`}>
            <div className="message-container">
                <div className={`avatar ${message.role === 'user' ? 'user-avatar' : 'bot-avatar'}`}>
                    {message.role === 'user' ? 'U' : 'T'}
                </div>
                <div className="message-content">
                    <ReactMarkdown>
                        {message.content}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
};

export default ChatMessage; 