// FAQSection.js
import React, { useState } from 'react';
import './FAQSection.css';

const FAQSection = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  const faqs = [
    {
      question: "Как пользоваться вашим сервисом?",
      answer: "Наш сервис прост в использовании. Зарегистрируйтесь, выберите нужные опции и следуйте инструкциям на экране."
    },
    {
      question: "Какие способы оплаты вы принимаете?",
      answer: "Мы принимаем кредитные карты, PayPal и банковские переводы."
    },
    {
      question: "Как долго занимает доставка?",
      answer: "Обычно доставка занимает 2-5 рабочих дней в зависимости от вашего местоположения."
    },
    {
      question: "Могу ли я вернуть товар?",
      answer: "Да, у нас есть 30-дневная гарантия возврата. Свяжитесь с нашей службой поддержки для получения инструкций."
    }
  ];

  const toggleFAQ = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <div className="faq-section">
      <h2>Часто задаваемые вопросы</h2>
      <div className="faq-list">
        {faqs.map((faq, index) => (
          <div
            className={`faq-item ${activeIndex === index ? 'active' : ''}`}
            key={index}
          >
            <div
              className="faq-question"
              onClick={() => toggleFAQ(index)}
            >
              {faq.question}
              <span className="faq-icon">{activeIndex === index ? '−' : '+'}</span>
            </div>
            {activeIndex === index && (
              <div className="faq-answer">{faq.answer}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FAQSection;