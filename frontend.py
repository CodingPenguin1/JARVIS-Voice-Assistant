#!/usr/bin/env python
import speech_recognition as sr
from gtts import gTTS
import os
import socket
import json

HOST = "127.0.0.1"
PORT = 22222


def sendCommand(sentence):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(sentence.encode())
        data = s.recv(1024)
    return data.decode('utf-8')


def say(sentence):
    print(sentence)
    tts = gTTS(sentence, 'en-uk')
    tts.save('.said.mp3')
    os.system('mpg123 .said.mp3')
    os.remove('.said.mp3')


def readConfig():
    with open("commands.json", "r") as commandsFile:
        info = json.load(commandsFile)
    return info


if __name__ == '__main__':
    # Set up recognizer and input device
    r = sr.Recognizer()
    mic = sr.Microphone()
    print(100*'\n')
    print('Detected microphones:\n{}'.format(sr.Microphone.list_microphone_names()))

    # Load config
    print('Loading config:')
    config = readConfig()
    print(config)
    assistantName = config['name']

    # Main Loop
    with mic as source:
        r.adjust_for_ambient_noise(source)
        while True:
            # Listen for input
            print('Listening...')
            audio = r.listen(source)
            # Once input is heard, try google first, then sphinx (if no internet connection or somehow Google fails)
            # try:
            #     heardSentence = r.recognize_google(audio).replace('sudo', 'PSEUDO')
            #     print('Using Google:')
            # except:
            heardSentence = r.recognize_sphinx(audio, show_all=True)
            for data, i in zip(heardSentence.nbest(), range(10)):
                heardSentence = data.hypstr
                break
            heardSentence = heardSentence.replace('sudo', 'PSEUDO')
            print('Using Sphinx:')
            print(heardSentence)

            # Send command to backend and get response
            returnedData = sendCommand(heardSentence.replace(assistantName, '').strip())
            print(returnedData)

            if 'stop' in heardSentence:
                quit()


