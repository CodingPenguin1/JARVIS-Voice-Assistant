#!/usr/bin/env python
import speech_recognition as sr
from gtts import gTTS
import os


def say(sentence):
    print(sentence)
    tts = gTTS(sentence, 'en-uk')
    tts.save('.said.mp3')
    os.system('mpg123 .said.mp3')
    os.remove('.said.mp3')

if __name__ == '__main__':
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)
        # say('Ready')
        while True:
            try:
                print('Listening...')
                audio = r.listen(source)
                print(r.recognize_sphinx(audio))
            except:
                print('Failed')

        # while True:
        #     try:
        #         print('Listening...')
        #         audio = r.listen(source)
        #         say('I heard you say: ' + r.recognize_google(audio, show_all=True))
        #     except:
        #         print("I didn't catch that")
