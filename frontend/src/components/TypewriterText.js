import React, { useState, useEffect, useRef } from 'react';
import '../styles/TypewriterText.css';

const TypewriterText = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');
  const intervalRef = useRef(null);

  // Функция для очистки текста от проблем
  const cleanText = (inputText) => {
    if (!inputText || typeof inputText !== 'string') return '';

    // Удаляем "undefined" в конце
    let cleaned = inputText.replace(/undefined$/, '');

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
      cleaned = cleaned.replace(new RegExp(typo, 'g'), correction);
    });

    return cleaned;
  };

  useEffect(() => {
    if (!text || typeof text !== 'string') {
      console.error('Invalid text received:', text);
      setDisplayedText('Произошла ошибка при получении ответа.');
      return;
    }

    // Очищаем текст от проблем
    const cleanedText = cleanText(text);

    // Сбрасываем состояние при изменении текста
    setDisplayedText('');
    let currentIndex = 0;

    // Очищаем предыдущий интервал, если он существует
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Эффект печатной машинки
    intervalRef.current = setInterval(() => {
      if (currentIndex < cleanedText.length) {
        setDisplayedText(prev => prev + cleanedText[currentIndex]);
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

  // Дополнительная проверка перед рендерингом
  const finalText = displayedText.replace(/undefined$/, '');

  return <p className="typewriter-text">{finalText}</p>;
};

export default TypewriterText;