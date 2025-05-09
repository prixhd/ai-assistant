import React, { useState } from 'react';
import VoiceAssistant from './components/VoiceAssistant';
import FAQSection from './components/FAQSection';
import './styles/App.css';

function App() {
    const [storeId, setStoreId] = useState('test-store');
    const [activeTab, setActiveTab] = useState('assistant');

    return (
        <div className="app">
            <header className="app-header">
                <div className="logo">
                    <h1>Хей-Хай</h1>
                </div>
                <div className="store-selector">
                    <label htmlFor="store-select">Магазин:</label>
                    <select
                        id="store-select"
                        value={storeId}
                        onChange={(e) => setStoreId(e.target.value)}
                    >
                        <option value="test-store">Горный Орёл</option>
                        <option value="store-2">Горный Сокол</option>
                    </select>
                </div>
            </header>

            <div className="tabs">
                <button
                    className={activeTab === 'assistant' ? 'active' : ''}
                    onClick={() => setActiveTab('assistant')}
                >
                    Ассистент
                </button>
                <button
                    className={activeTab === 'faq' ? 'active' : ''}
                    onClick={() => setActiveTab('faq')}
                >
                    Вопросы и ответы
                </button>
            </div>

            <main className="app-content">
                {activeTab === 'assistant' ? (
                    <VoiceAssistant storeId={storeId} />
                ) : (
                    <FAQSection />
                )}
            </main>

            <footer className="app-footer">
                <p>© 2025 Хей-Хай Ассистент</p>
            </footer>
        </div>
    );
}

export default App;