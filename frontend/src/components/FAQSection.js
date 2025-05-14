import React, { useState, useEffect } from 'react';
import { getFaqs } from '../api/api';
import '../styles/FAQSection.css';

const FAQSection = () => {
  const [faqs, setFaqs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadFaqs = async () => {
      try {
        const data = await getFaqs();
        setFaqs(data);
      } catch (error) {
        console.error('Error loading FAQs:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadFaqs();
  }, []);

  if (isLoading) {
    return <div className="faq-loading">Загрузка часто задаваемых вопросов...</div>;
  }

  return (
    <div className="faq-section">
      <h2>Часто задаваемые вопросы</h2>

      {faqs.length === 0 ? (
        <p>Нет доступных вопросов и ответов.</p>
      ) : (
        <div className="faq-list">
          {faqs.map((faq, index) => (
            <div key={index} className="faq-item">
              <h3>{faq.question}</h3>
              <p>{faq.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FAQSection;