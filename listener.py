import speech_recognition as sr


def listen(self):
    r = sr.Recognizer()
    mic = sr.Microphone()

    if not self.ready:
        self.say(self.preferences['startupQuote'])
        self.ready = True

    with mic as source:
        print('\nlistening')
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source)
            saidSentence = r.recognize_google(audio).lower()
            print('Heard: ' + saidSentence)
            self.act(saidSentence)
        except:
            print("I didn't catch that")



if __name__ == '__main__':
    while True:
        listen()
