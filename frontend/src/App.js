import React, { useState } from 'react';
import ChatButton from './components/ChatButton';
import ChatInterface from './components/ChatInterface';
import './styles/App.css';

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleModal = () => {
    setIsModalOpen(!isModalOpen);
  };

  return (
    <div className="app">
      {/* Кнопка чата в правом нижнем углу */}
      <ChatButton onClick={toggleModal} />

      {/* Модальное окно чата */}
      <ChatInterface isOpen={isModalOpen} onClose={toggleModal} />
    </div>
  );
}

export default App;