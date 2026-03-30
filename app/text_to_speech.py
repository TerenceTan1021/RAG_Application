# app/text_to_speech.py
import pyttsx3
import tempfile
import os
from gtts import gTTS
import playsound
import threading

class TextToSpeech:
    def __init__(self, engine="gtts"):
        self.engine = engine
        if engine == "pyttsx3":
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
    
    def speak_gtts(self, text, lang='en'):
        """Use Google Text-to-Speech (requires internet)"""
        def play_audio():
            try:
                tts = gTTS(text=text, lang=lang, slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    temp_file = fp.name
                    tts.save(temp_file)
                    playsound.playsound(temp_file)
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Error in TTS: {e}")
        
        thread = threading.Thread(target=play_audio)
        thread.start()
        return thread
    
    def speak_pyttsx3(self, text):
        """Use offline text-to-speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")
    
    def speak(self, text, lang='en'):
        """Speak text using selected engine"""
        if self.engine == "gtts":
            return self.speak_gtts(text, lang)
        else:
            self.speak_pyttsx3(text)
    
    def speak_document_section(self, document_text, chunk_size=500):
        """Speak a document section by section"""
        chunks = [document_text[i:i+chunk_size] for i in range(0, len(document_text), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            print(f"Reading section {i+1}/{len(chunks)}")
            self.speak(chunk)
            if i < len(chunks) - 1:
                input("Press Enter to continue to next section...")