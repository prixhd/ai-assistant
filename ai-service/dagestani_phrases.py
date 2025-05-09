import random

# Дагестанские выражения
PHRASES = [
    "Валлах",
    "Биллях",
    "Машаллах",
    "Клянусь",
    "Чёткий",
    "Красавчик"
]

# Дагестанские окончания
ENDINGS = [
    ", брат",
    ", уважаемый",
    ", дорогой",
    ", джигит",
    ", да"
]

def add_dagestani_style(text):
    """Добавление дагестанского стиля к тексту"""
    if not text:
        return text

    sentences = text.split('. ')
    styled_sentences = []

    for i, sentence in enumerate(sentences):
        if not sentence:
            continue

        # Добавляем выражение в начало с шансом 30%
        if i == 0 or random.random() < 0.3:
            prefix = random.choice(PHRASES) + ", "
            sentence = prefix + sentence[0].lower() + sentence[1:]

        # Добавляем окончание с шансом 40%
        if random.random() < 0.4:
            sentence += random.choice(ENDINGS)

        styled_sentences.append(sentence)

    return '. '.join(styled_sentences)