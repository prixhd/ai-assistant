import React, { useRef, useEffect } from 'react';
import '../styles/AnimatedSphere.css';

const AnimatedSphere = ({ isActive }) => {
  const sphereRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (!sphereRef.current) return;

    // Если активен голосовой ввод, добавляем класс для анимации
    if (isActive) {
      sphereRef.current.classList.add('sphere-active');

      // Имитация эквалайзера (можно заменить на реальный анализ звука)
      let scale = 1;
      const animate = () => {
        if (!sphereRef.current) return;

        // Случайное изменение размера для имитации реакции на звук
        scale = 1 + Math.random() * 0.3;
        sphereRef.current.style.transform = `scale(${scale})`;

        animationRef.current = requestAnimationFrame(animate);
      };

      animationRef.current = requestAnimationFrame(animate);
    } else {
      // Если голосовой ввод не активен, убираем анимацию
      sphereRef.current.classList.remove('sphere-active');
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        sphereRef.current.style.transform = 'scale(1)';
      }
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);

  return (
    <div className={`sphere-wrapper ${isActive ? 'active' : ''}`}>
      <div className="sphere" ref={sphereRef}></div>
    </div>
  );
};

export default AnimatedSphere;