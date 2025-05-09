import axios from 'axios';

// Определяем API URL
const API_URL = 'http://localhost:5001';

console.log("Using AI Service URL:", API_URL);

// Функция для отправки сообщения на бэкенд
export const sendMessage = async (message) => {
  try {
    console.log('Processing message:', message);

    // Отправляем POST запрос напрямую
    const response = await axios.post(`${API_URL}/process`, { message }, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000  // Увеличиваем до 40 секунд
    });

    console.log('AI response received:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error.message);  // Выводим только сообщение об ошибке

    // Более подробная обработка ошибок
    if (error.code === 'ECONNABORTED') {
      return { response: "Запрос занял слишком много времени. Пожалуйста, попробуйте еще раз." };
    }

    // Если произошла ошибка с ответом
    if (error.response && error.response.data && error.response.data.error) {
      return { response: error.response.data.error };
    }

    // Если произошла другая ошибка
    return { response: "Извините, произошла техническая ошибка. Пожалуйста, попробуйте позже." };
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