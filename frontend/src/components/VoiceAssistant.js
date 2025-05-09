import React, { useState, useEffect, useRef } from 'react';
import { sendMessage } from '../services/api';
import './VoiceAssistant.css';

const VoiceAssistant = () => {
  const [isListening, setIsListening] = useState(false);
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const recognitionRef = useRef(null);
  const messageEndRef = useRef(null);

  // Прокрутка к последнему сообщению
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  // Остановка распознавания при размонтировании компонента
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          console.error('Ошибка при остановке распознавания:', e);
        }
      }
    };
  }, []);

  const startListening = () => {
    try {
      // Проверяем поддержку распознавания речи
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognition) {
        setError('Ваш браузер не поддерживает распознавание речи');
        return;
      }

      // Останавливаем предыдущее распознавание, если оно активно
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          console.error('Ошибка при остановке предыдущего распознавания:', e);
        }
      }

      // Создаем новый экземпляр распознавания
      recognitionRef.current = new SpeechRecognition();
      const recognition = recognitionRef.current;

      // Настройка параметров
      recognition.lang = 'ru-RU';
      recognition.continuous = false;
      recognition.interimResults = false;

      // Обработчики событий
      recognition.onstart = () => {
        setIsListening(true);
        setError(null);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setMessage(transcript);
        handleSendMessage(transcript);
      };

      recognition.onerror = (event) => {
        console.error('Ошибка распознавания речи:', event.error);

        if (event.error === 'network') {
          setError('Проблема с сетью. Пожалуйста, проверьте подключение к интернету или введите сообщение вручную.');
        } else if (event.error === 'not-allowed') {
          setError('Доступ к микрофону запрещен. Пожалуйста, разрешите доступ к микрофону в настройках браузера.');
        } else if (event.error === 'no-speech') {
          setError('Речь не распознана. Пожалуйста, говорите громче или используйте текстовый ввод.');
        } else {
          setError(`Ошибка распознавания речи: ${event.error}`);
        }

        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      // Запускаем распознавание
      recognition.start();

    } catch (error) {
      console.error('Ошибка при инициализации распознавания речи:', error);
      setError('Не удалось запустить распознавание речи. Пожалуйста, введите сообщение вручную.');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        console.error('Ошибка при остановке распознавания:', e);
      }
    }
    setIsListening(false);
  };

  const handleSendMessage = async (text) => {
    if (!text || text.trim() === '') return;

    const userMessage = text.trim();
    setMessage('');
    setIsLoading(true);

    // Добавляем сообщение пользователя в историю
    setHistory(prev => [...prev, { type: 'user', text: userMessage }]);

    try {
      // Отправляем запрос к API
      const result = await sendMessage(userMessage);

      if (result && result.response) {
        setResponse(result.response);
        // Добавляем ответ ассистента в историю
        setHistory(prev => [...prev, { type: 'assistant', text: result.response }]);
      } else {
        throw new Error('Неверный формат ответа');
      }
    } catch (error) {
      console.error('Ошибка при отправке сообщения:', error);
      setError('Не удалось получить ответ. Пожалуйста, попробуйте еще раз.');
      // Добавляем сообщение об ошибке в историю
      setHistory(prev => [...prev, { type: 'error', text: 'Не удалось получить ответ. Пожалуйста, попробуйте еще раз.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage(message);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    setResponse('');
    setError(null);
  };

  return (
    <div className="voice-assistant">
      <h2>Голосовой ассистент</h2>

      {/* История сообщений */}
      <div className="chat-history">
        {history.length === 0 ? (
          <div className="empty-history">
            <p>Начните разговор с ассистентом</p>
          </div>
        ) : (
          history.map((item, index) => (
            <div key={index} className={`message ${item.type}`}>
              <div className="message-content">
                <span className="message-sender">
                  {item.type === 'user' ? 'Вы' :
                   item.type === 'assistant' ? 'Ассистент' : 'Система'}:
                </span>
                <p>{item.text}</p>
              </div>
            </div>
          ))
        )}
        <div ref={messageEndRef} />
      </div>

      {/* Сообщение об ошибке */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button className="close-error" onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Индикатор загрузки */}
            {isLoading && (
              <div className="loading-indicator">
                <div className="loading-spinner"></div>
                <p>Получение ответа...</p>
              </div>
            )}

            {/* Элементы управления */}
            <div className="voice-controls">
              {/* Кнопки управления голосом */}
              <div className="voice-buttons">
                {!isListening ? (
                  <button
                    className="voice-btn start"
                    onClick={startListening}
                    disabled={isLoading}
                  >
                    <i className="mic-icon"></i>
                    Говорите
                  </button>
                ) : (
                  <button
                    className="voice-btn stop"
                    onClick={stopListening}
                  >
                    <i className="stop-icon"></i>
                    Остановить
                  </button>
                )}
              </div>

              {/* Текстовый ввод */}
              <div className="text-input">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Введите сообщение..."
                  disabled={isLoading || isListening}
                />
                <button
                  className="send-btn"
                  onClick={() => handleSendMessage(message)}
                  disabled={isLoading || message.trim() === ''}
                >
                  Отправить
                </button>
              </div>

              {/* Кнопка очистки истории */}
              {history.length > 0 && (
                <button
                  className="clear-btn"
                  onClick={clearHistory}
                  disabled={isLoading}
                >
                  Очистить историю
                </button>
              )}
            </div>

            {/* Подсказки */}
            <div className="assistant-tips">
              <h3>Примеры вопросов:</h3>
              <ul>
                <li onClick={() => setMessage("Какие товары у вас есть в наличии?")}>
                  Какие товары у вас есть в наличии?
                </li>
                <li onClick={() => setMessage("Как оформить заказ?")}>
                  Как оформить заказ?
                </li>
                <li onClick={() => setMessage("Какие есть способы доставки?")}>
                  Какие есть способы доставки?
                </li>
              </ul>
            </div>
          </div>
        );
      };

      export default VoiceAssistant;