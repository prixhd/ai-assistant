// src/components/ChatInterface.js
import React, { useState, useEffect, useRef } from 'react';
import AudioEqualizer from './AudioEqualizer';
import VoiceInput from './VoiceInput';
import ChatMessages from './ChatMessages';
import { sendMessage, clearChatSession } from '../api/api';
import '../styles/ChatInterface.css';

const ChatInterface = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const modalRef = useRef(null);

  // Загружаем сообщения из localStorage при монтировании компонента
  useEffect(() => {
    const savedMessages = localStorage.getItem('chat_messages');
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Error parsing saved messages:', e);
        localStorage.removeItem('chat_messages');
      }
    }
  }, []);

  // Сохраняем сообщения в localStorage при их изменении
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chat_messages', JSON.stringify(messages));
    }
  }, [messages]);

  // Закрытие модального окна при клике вне его
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  // Обработка отправки сообщения
  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // Добавляем сообщение пользователя
    const userMessage = { text, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Отправляем запрос к AI
      const response = await sendMessage(text);

      // Добавляем ответ AI
      if (response && response.response) {
        // Очищаем ответ от возможного "undefined" в конце
        let aiResponse = response.response;

        // Проверяем, что ответ не содержит "undefined"
        if (typeof aiResponse === 'string') {
          // Удаляем "undefined" в конце строки
          aiResponse = aiResponse.replace(/undefined$/, '');
        }

        const aiMessage = { text: aiResponse, isUser: false };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        text: 'Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.',
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Обработка голосового ввода
  const handleVoiceInput = (transcript) => {
    if (transcript) {
      handleSendMessage(transcript);
    }
  };

  // Обработка текстового ввода
  const handleTextSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputText);
  };

  // Очистка истории диалога
  const handleClearChat = async () => {
    try {
      const result = await clearChatSession();
      if (result.success) {
        setMessages([]);
        localStorage.removeItem('chat_messages');
        // Добавляем системное сообщение о начале нового диалога
        setMessages([{
          text: 'История диалога очищена. Начинаем новый разговор!',
          isUser: false,
          isSystem: true
        }]);
      } else {
        console.error('Failed to clear chat session:', result.message);
      }
    } catch (error) {
      console.error('Error clearing chat session:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="chat-modal-overlay">
      <div className="chat-modal" ref={modalRef}>
        <div className="chat-header">
          <div className="chat-title">
            <span>Ассистент</span>
          </div>
          <div className="chat-controls">
            <button className="clear-button" onClick={handleClearChat} title="Очистить историю диалога">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6H5H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="close-button" onClick={onClose}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <div className="chat-content">
          <div className="equalizer-container">
            <AudioEqualizer isActive={isListening} />
          </div>

          <ChatMessages messages={messages} isLoading={isLoading} />

          <div className="input-container">
            <form onSubmit={handleTextSubmit} className="text-input-form">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Введите сообщение..."
                className="text-input"
              />
              <button type="submit" className="send-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </form>

            <VoiceInput
              onTranscript={handleVoiceInput}
              isListening={isListening}
              setIsListening={setIsListening}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;