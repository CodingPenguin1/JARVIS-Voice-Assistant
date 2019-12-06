#!/usr/bin/env python
import speech_recognition as sr
from gtts import gTTS
import os


def say(sentence):
    print('Heard:', sentence)
    tts = gTTS(sentence, 'en-uk')
    tts.save('.said.mp3')
    os.system('mpg123 .said.mp3')
    os.remove('.said.mp3')

if __name__ == '__main__':
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)

    with mic as source:
        print('adjusting')
        r.adjust_for_ambient_noise(source)
        say('Ready')
        
        while True:
            print('looping')
            try:
                print('try')
                audio = r.listen(source)
                print('done listening')
                say('I heard you say: ' + r.recognize_google(audio))
            except:
                print("I didn't catch that")
