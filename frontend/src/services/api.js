import axios from 'axios';

// Определяем API URL
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:5001'
  : `${window.location.protocol}//${window.location.hostname}:5001`;

console.log("Using AI Service URL:", API_URL);

export const sendMessage = async (message) => {
  try {
    console.log('Processing message:', message);

    // Отправляем POST запрос с увеличенным таймаутом
    const response = await axios.post(`${API_URL}/process`, { message }, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      timeout: 90000  // Увеличиваем до 90 секунд
    });

    console.log('AI response received:', response.data);
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

export default { sendMessage, getFaqs };