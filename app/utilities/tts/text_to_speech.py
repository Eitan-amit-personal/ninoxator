import pyttsx3
import os


if os.name != 'nt':
    speech_engine = pyttsx3.init()
    # voices = speech_engine.getProperty('voices')
    # speech_engine.setProperty('voice', voices[1].id)    # change to female voice
    speech_engine.setProperty('rate', 173)


def speech_say(text: str):
    if os.name != 'nt':
        speech_engine.say(text)
        speech_engine.runAndWait()
