// Проверка поддержки распознавания речи в браузере
export const isSpeechRecognitionSupported = () => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
};

// Создание экземпляра распознавания речи
export const createSpeechRecognition = () => {
  if (!isSpeechRecognitionSupported()) {
    console.error('Speech recognition is not supported in this browser');
    return null;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'ru-RU';

  return recognition;
};