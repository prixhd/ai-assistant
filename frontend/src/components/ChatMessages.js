import React, { useRef, useEffect } from 'react';
import TypewriterText from './TypewriterText';
import '../styles/ChatMessages.css';

const ChatMessages = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  // Автоматическая прокрутка к последнему сообщению
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="chat-messages">
      {messages.length === 0 ? (
        <div className="empty-chat">
          <p>Привет! Я голосовой помощник. Чем могу помочь?</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.isUser ? 'user-message' : 'ai-message'}`}
          >
            <div className="message-content">
              {message.isUser ? (
                <p>{message.text}</p>
              ) : (
                <TypewriterText text={message.text} />
              )}
            </div>
          </div>
        ))
      )}

      {isLoading && (
        <div className="message ai-message">
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatMessages;