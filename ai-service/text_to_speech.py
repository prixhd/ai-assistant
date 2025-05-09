import gtts

def text_to_speech(text, output_path):
    """
    Преобразование текста в речь с использованием Google Text-to-Speech
    """
    try:
        tts = gtts.gTTS(text=text, lang='ru', slow=False)
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"Ошибка при конвертации текста в речь: {e}")
        return False