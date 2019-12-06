#!/usr/bin/env python
import speech_recognition as sr
from gtts import gTTS
import os
import socket
import json
import argparse


def sendCommand(sentence, s):
    s.sendall(sentence.encode())
    data = s.recv(1024).decode('utf-8')
    return data


def say(sentence, language, pitch, speed):
    print('Saying:', sentence)
    os.system('espeak "{}" -v {} -p {} -s {}'.format(sentence, language, pitch, speed))


def readConfig(configFilepath):
    with open(configFilepath, 'r') as commandsFile:
        info = json.load(commandsFile)
    return info

def getAudio(mic, recognizer):
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = r.non_speaking_duration

        # Listen for input
        print('\n\nListening...')
        try:
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=10)
        except:
            # If longer than 5 seconds of silence, retry
            heardSentence = ''

        # Once input is heard, try google first, then sphinx (if no internet connection or somehow Google fails)
        try:
            try:
                print('Trying Google')
                heardSentence = recognizer.recognize_google(audio).lower()
                print('Using Google:')
            except:
                print('Trying Sphinx')
                heardSentence = recognizer.recognize_sphinx(audio, show_all=True)
                for data, i in zip(heardSentence.nbest(), range(10)):
                    heardSentence = data.hypstr.lower()
                    break
                print('Using Sphinx:')
        except:
            heardSentence = ''
        if len(heardSentence) > 0:
            print(heardSentence)
    return heardSentence


def stop(language, pitch, speed, socket):
    sendCommand('please shoot yourself in the foot', socket)
    say('Goodbye, Sir', language, pitch, speed)
    quit()


if __name__ == '__main__':
    # Global vars
    HOST = '127.0.0.1'
    PORT = 22222
    CONFIG = 'commands.json'

    # CLI args for global vars (frontend is initialized by the backend)
    parser = argparse.ArgumentParser(description='Voice Assistant Frontend')
    parser.add_argument('--ip', type=str, help='IP of the system the backend is running on')
    parser.add_argument('--port', type=int, help='Port to communicate on')
    parser.add_argument('--config', type=str, help='Config filepath')
    args = parser.parse_args()

    # Set up recognizer and input device
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=0)
    print(100*'\n')
    print('Detected microphones:\n{}\n\n'.format(sr.Microphone.list_microphone_names()))

    # Parsing CLI Args
    HOST = args.ip if args.ip is not None else HOST
    PORT = args.port if args.port is not None else PORT
    CONFIG = args.config if args.config is not None else CONFIG
    print('HOST:', HOST)
    print('PORT:', PORT)
    print('CONFIG:', CONFIG)

    # Load config
    print('\n\nConfiguration:')
    config = readConfig(CONFIG)
    print(config, '\n\n')
    assistantName = config['name']
    language = config['language']
    pitch = config['pitch']
    speed = config['speed']

    # Say startup quote and begin running
    say(config['startupQuote'], language, pitch, speed)

    # Main Loop
    while True:
        heardSentence = getAudio(mic, r)
        heardSentence = str(heardSentence).lower()

        # Process sentence
        if len(heardSentence) > 0:
            if assistantName.lower() in heardSentence:
                heardSentence = heardSentence.replace(assistantName, '').strip()
                if len(heardSentence) > 0:
                    heardSentence = heardSentence.replace('sudo', 'PSEUDO')

                    # Send command to backend and get response
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((HOST, PORT))
                        if 'stop' in heardSentence:
                            stop(language, pitch, speed, s)
                        returnedData = sendCommand(heardSentence, s)
                        say(returnedData, language, pitch, speed)
                        
                        while True:
                            data = s.recv(1024).decode('utf-8')
                            if config["clarificationMessage"] in data:
                                # Listen for input
                                print("Getting calrification: '{}'".format(data))
                                say(data.replace(config["clarificationMessage"], ''), language, pitch, speed)
                                while True:
                                    heardSentence = getAudio(mic, r)
                                    heardSentence = str(heardSentence).lower().strip()
                                    if len(heardSentence) > 0:
                                        if 'stop' in heardSentence:
                                            stop(language, pitch, speed, s)
                                        returnedData = sendCommand(heardSentence, s)
                                        say(returnedData, language, pitch, speed)
                                        break
                            else:
                                break
