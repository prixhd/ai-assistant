import React, { useState, useEffect, useRef } from 'react';
import AnimatedSphere from './AnimatedSphere';
import VoiceInput from './VoiceInput';
import ChatMessages from './ChatMessages';
import { sendMessage } from '../api/api';
import '../styles/ChatInterface.css';

const ChatInterface = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const modalRef = useRef(null);

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

          // Исправляем типичные опечатки
          const typoCorrections = {
            "Врианты": "Варианты",
            "Заскамиь": "Заскочи",
            "хошь": "хочешь",
            "тыщ": "тысяч",
            "Всь": "Вот",
            "Валейкум": "Ваалейкум"
          };

          Object.entries(typoCorrections).forEach(([typo, correction]) => {
            aiResponse = aiResponse.replace(new RegExp(typo, 'g'), correction);
          });
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

  if (!isOpen) return null;

  return (
    <div className="chat-modal-overlay">
      <div className="chat-modal" ref={modalRef}>
        <div className="chat-header">
          <div className="chat-title">
            <span>Ассистент</span>
          </div>
          <button className="close-button" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        <div className="chat-content">
          <div className="sphere-container">
            <AnimatedSphere isActive={isListening} />
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
                  <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
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