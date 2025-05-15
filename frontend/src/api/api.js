import axios from 'axios';

// Определяем API URL
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:5001'
  : `${window.location.protocol}//${window.location.hostname}:5001`;

console.log("Using AI Service URL:", API_URL);

// Получаем или создаем session_id
const getSessionId = () => {
  let sessionId = localStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Date.now();
    localStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
};

export const sendMessage = async (message) => {
  try {
    console.log('Processing message:', message);

    // Получаем session_id
    const sessionId = getSessionId();

    // Отправляем POST запрос с увеличенным таймаутом и session_id
    const response = await axios.post(`${API_URL}/process`, {
      message,
      session_id: sessionId
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      timeout: 90000  // Увеличиваем до 90 секунд
    });

    console.log('AI response received:', response.data);

    // Если сервер вернул новый session_id, сохраняем его
    if (response.data && response.data.session_id) {
      localStorage.setItem('chat_session_id', response.data.session_id);
    }

    // Очищаем ответ от "undefined"
    if (response.data && response.data.response) {
      if (typeof response.data.response === 'string' && response.data.response.endsWith('undefined')) {
        response.data.response = response.data.response.replace(/undefined$/, '');
      }
    }

    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);

    // Более подробная обработка ошибок
    if (error.code === 'ECONNABORTED') {
      return { response: "Запрос занял слишком много времени. Пожалуйста, попробуйте еще раз." };
    }

        if (error.response) {
          // Сервер ответил с кодом ошибки
          return { response: `Ошибка сервера: ${error.response.status}. Пожалуйста, попробуйте позже.` };
        } else if (error.request) {
          // Запрос был сделан, но ответа не получено
          return { response: "Сервер не отвечает. Пожалуйста, проверьте соединение." };
        } else {
          // Что-то пошло не так при настройке запроса
          return { response: "Произошла ошибка при отправке запроса." };
        }
      }
    };

    // Функция для очистки истории диалога
    export const clearChatSession = async () => {
      try {
        const sessionId = getSessionId();

        const response = await axios.post(`${API_URL}/clear-session`, {
          session_id: sessionId
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        console.log('Session cleared:', response.data);
        return { success: true, message: "История диалога очищена" };
      } catch (error) {
        console.error('Error clearing session:', error);
        return { success: false, message: "Не удалось очистить историю диалога" };
      }
    };

    export const getFaqs = async () => {
      try {
        console.log('Fetching FAQs');
        const response = await axios.get('http://localhost:8080/api/faqs');
        console.log('FAQ response:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error fetching FAQs:', error);
        // Возвращаем пустой массив при ошибке
        return [];
      }
    };

    export default { sendMessage, clearChatSession, getFaqs };