from googletrans import Translator

translator = Translator()

def translate_text(text, dest_lang="en"):
    try:
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except Exception as e:
        return f"Translation error: {e}"
