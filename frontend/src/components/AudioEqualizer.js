// src/components/AudioEqualizer.js
import React, { useRef, useEffect } from 'react';
import '../styles/Equalizer.css';

const AudioEqualizer = ({ isActive }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const sourceRef = useRef(null);
  const streamRef = useRef(null);
  const barValuesRef = useRef([0, 0, 0, 0]); // Для плавной анимации

  // Инициализация Web Audio API
  useEffect(() => {
    if (isActive) {
      try {
        // Создаем аудио контекст
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContextRef.current = new AudioContext();

        // Создаем анализатор
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 32; // Маленький размер FFT для 4 полос

        // Создаем буфер для данных
        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);

        // Получаем доступ к микрофону
        navigator.mediaDevices.getUserMedia({ audio: true, video: false })
          .then(stream => {
            streamRef.current = stream;

            // Создаем источник из потока микрофона
            sourceRef.current = audioContextRef.current.createMediaStreamSource(stream);

            // Подключаем источник к анализатору
            sourceRef.current.connect(analyserRef.current);
          })
          .catch(err => {
            console.error('Ошибка доступа к микрофону:', err);
            // Если не удалось получить доступ к микрофону, используем фейковые данные
            dataArrayRef.current = null;
          });
      } catch (err) {
        console.error('Ошибка инициализации Web Audio API:', err);
        audioContextRef.current = null;
        analyserRef.current = null;
        dataArrayRef.current = null;
      }
    } else {
      // Очищаем ресурсы при деактивации
      if (sourceRef.current) {
        sourceRef.current.disconnect();
        sourceRef.current = null;
      }

      if (streamRef.current) {
        // Останавливаем все треки в потоке
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(err => console.error('Ошибка закрытия аудио контекста:', err));
        audioContextRef.current = null;
      }
    }

    // Очистка при размонтировании
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }

      if (sourceRef.current) {
        sourceRef.current.disconnect();
        sourceRef.current = null;
      }

      if (streamRef.current) {
        // Останавливаем все треки в потоке
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(err => console.error('Ошибка закрытия аудио контекста:', err));
        audioContextRef.current = null;
      }
    };
  }, [isActive]);

  // Отрисовка эквалайзера
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;

    // Устанавливаем размеры canvas с учетом плотности пикселей
    canvas.width = 200 * dpr; // Уменьшаем ширину canvas
    canvas.height = 100 * dpr; // Уменьшаем высоту canvas
    ctx.scale(dpr, dpr);

    // Определяем параметры эквалайзера
    const numBars = 4;
    const dotRadius = 4; // Уменьшаем размер точек
    const barWidth = dotRadius * 2; // Ширина полосы равна диаметру точки
    const spacing = 16; // Уменьшаем расстояние между точками
    const startX = (200 - (numBars - 1) * spacing) / 2;
    const centerY = 50; // Центрируем по новой высоте

    // Полный набор цветов градиента
    const colors = {
      color0: '#4BC4FF',   // 0%
      color26: '#1A9AFF',  // 26%
      color56: '#BE64FE',  // 56%
      color75: '#EF5794',  // 75%
      color85: '#FD683F',  // 85%
      color94: '#FE7C2B',  // 94%
      color100: '#FFA10B'  // 100%
    };

    // Функция для плавного изменения значений
    const smoothValue = (target, current, factor = 0.15) => {
      return current + (target - current) * factor;
    };

    // Функция для отрисовки палки с закругленными концами
    const drawRoundedBar = (x, y1, y2, width, radius) => {
      // y1 - верхняя точка, y2 - нижняя точка
      const height = y2 - y1;

      ctx.beginPath();
      // Верхний левый угол (закругленный)
      ctx.moveTo(x - width/2 + radius, y1);
      // Верхняя сторона
      ctx.lineTo(x + width/2 - radius, y1);
      // Верхний правый угол (закругленный)
      ctx.arc(x + width/2 - radius, y1 + radius, radius, -Math.PI/2, 0, false);
      // Правая сторона
      ctx.lineTo(x + width/2, y2 - radius);
      // Нижний правый угол (закругленный)
      ctx.arc(x + width/2 - radius, y2 - radius, radius, 0, Math.PI/2, false);
      // Нижняя сторона
      ctx.lineTo(x - width/2 + radius, y2);
      // Нижний левый угол (закругленный)
      ctx.arc(x - width/2 + radius, y2 - radius, radius, Math.PI/2, Math.PI, false);
      // Левая сторона
      ctx.lineTo(x - width/2, y1 + radius);
      // Верхний левый угол (закругленный)
      ctx.arc(x - width/2 + radius, y1 + radius, radius, Math.PI, 3*Math.PI/2, false);

      ctx.closePath();
      ctx.fill();
    };

    // Функция для отрисовки эквалайзера
    const draw = () => {
      // Очищаем canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Получаем данные частот, если доступны
      let frequencyData = [];
      if (analyserRef.current && dataArrayRef.current && isActive) {
        analyserRef.current.getByteFrequencyData(dataArrayRef.current);

        // Берем только первые 4 значения или генерируем случайные, если данных недостаточно
        for (let i = 0; i < numBars; i++) {
          if (i < dataArrayRef.current.length) {
            frequencyData[i] = dataArrayRef.current[i];
          } else {
            frequencyData[i] = Math.random() * 255;
          }
        }
      } else {
        // Если анализатор недоступен или неактивен, используем минимальные значения
        for (let i = 0; i < numBars; i++) {
          frequencyData[i] = 0; // Минимальное значение для неактивного состояния
        }
      }

      // Отрисовываем каждую колонку эквалайзера
      for (let i = 0; i < numBars; i++) {
        const x = startX + i * spacing;

        // Плавно изменяем значения
        const targetValue = isActive ? frequencyData[i] / 255 : 0; // Нормализуем от 0 до 1, если неактивен - стремимся к 0
        barValuesRef.current[i] = smoothValue(targetValue, barValuesRef.current[i]);

        // Определяем высоту полос (с ограничением)
        const maxBarHeight = 25; // Уменьшаем максимальную высоту полосы
        const barHeight = barValuesRef.current[i] * maxBarHeight;

        // Отрисовываем полосу только если она видима
        if (barHeight > 1) {
          // Создаем градиент для всей полосы с полным набором цветов
          const gradient = ctx.createLinearGradient(x, centerY - barHeight - dotRadius, x, centerY + barHeight + dotRadius);
          gradient.addColorStop(0, colors.color0);     // 0%
          gradient.addColorStop(0.26, colors.color26); // 26%
          gradient.addColorStop(0.56, colors.color56); // 56%
          gradient.addColorStop(0.75, colors.color75); // 75%
          gradient.addColorStop(0.85, colors.color85); // 85%
          gradient.addColorStop(0.94, colors.color94); // 94%
          gradient.addColorStop(1, colors.color100);   // 100%

          ctx.fillStyle = gradient;

          // Отрисовываем единую палку с закругленными концами
          drawRoundedBar(
            x,
            centerY - barHeight - dotRadius,
            centerY + barHeight + dotRadius,
            barWidth,
            barWidth/2
          );
        } else {
          // Если полоса не видима, отрисовываем только точку
          ctx.beginPath();
          ctx.arc(x, centerY, dotRadius, 0, Math.PI * 2);
          ctx.fillStyle = isActive ? colors.color56 : '#000'; // Используем цвет из середины градиента для точки
          ctx.fill();
        }
      }

      // Продолжаем анимацию
      animationRef.current = requestAnimationFrame(draw);
    };

    // Запускаем анимацию
    draw();

    // Очистка при размонтировании
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [isActive]);

  return (
    <div className="equalizer-container">
      <canvas
        ref={canvasRef}
        className="equalizer-canvas"
        style={{ width: '200px', height: '100px' }} // Уменьшаем размеры canvas
      />
    </div>
  );
};

export default AudioEqualizer;