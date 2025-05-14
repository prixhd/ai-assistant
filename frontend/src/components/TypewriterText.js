import React, { useState, useEffect, useRef } from 'react';
import '../styles/TypewriterText.css';

const TypewriterText = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!text || typeof text !== 'string') {
      console.error('Invalid text received:', text);
      setDisplayedText('Произошла ошибка при получении ответа.');
      return;
    }

    // Сбрасываем состояние при изменении текста
    setDisplayedText('');
    let currentIndex = 0;

    // Очищаем предыдущий интервал, если он существует
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Эффект печатной машинки
    intervalRef.current = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(prev => prev + text[currentIndex]);
        currentIndex++;
      } else {
        clearInterval(intervalRef.current);
      }
    }, 30); // Скорость печати (мс)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [text]);

  return <p className="typewriter-text">{displayedText}</p>;
};

export default TypewriterText;