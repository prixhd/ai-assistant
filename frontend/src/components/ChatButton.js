// src/components/ChatButton.js
import React from 'react';
import '../styles/ChatButton.css';

const ChatButton = ({ onClick }) => {
  return (
    <button className="chat-button" onClick={onClick}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 13.5997 2.37562 15.1116 3.04346 16.4525C3.22094 16.8088 3.28001 17.2161 3.17712 17.6006L2.58151 19.8267C2.32295 20.793 3.20701 21.677 4.17335 21.4185L6.39939 20.8229C6.78393 20.72 7.19121 20.7791 7.54753 20.9565C8.88837 21.6244 10.4003 22 12 22Z" fill="white"/>
        <path d="M8 12H8.01M12 12H12.01M16 12H16.01M8.5 12C8.5 12.2761 8.27614 12.5 8 12.5C7.72386 12.5 7.5 12.2761 7.5 12C7.5 11.7239 7.72386 11.5 8 11.5C8.27614 11.5 8.5 11.7239 8.5 12ZM12.5 12C12.5 12.2761 12.2761 12.5 12 12.5C11.7239 12.5 11.5 12.2761 11.5 12C11.5 11.7239 11.7239 11.5 12 11.5C12.2761 11.5 12.5 11.7239 12.5 12ZM16.5 12C16.5 12.2761 16.2761 12.5 16 12.5C15.7239 12.5 15.5 12.2761 15.5 12C15.5 11.7239 15.7239 11.5 16 11.5C16.2761 11.5 16.5 11.7239 16.5 12Z" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </button>
  );
};

export default ChatButton;