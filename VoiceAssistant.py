import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import os


class VoiceAssistant:
    def __init__(self, name='jarvis', startupQuote='At your service, sir'):
        self.name = name
        self.say(startupQuote)

    def listen(self):
        r = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print('listening')
            # r.adjust_for_ambient_noise(source)
            try:
                audio = r.listen(source)
                saidSentence = r.recognize_google(audio).lower()
                self.act(saidSentence)
            except:
                print("I didn't catch that")

    def say(self, sentence):
        # Generate audio file
        tts = gTTS(sentence, 'en-uk')
        tts.save('.said.mp3')
        silenceDelay = AudioSegment.silent(duration=2000)
        said = AudioSegment.from_mp3('.said.mp3')
        said = silenceDelay + said
        said.export('.said.mp3', format='mp3')

        # Play audio file
        os.system('mpg123 .said.mp3')

        # Delete audio file
        os.remove('.said.mp3')

    def act(self, instructions):
        # Make sure the assistant has been summoned:
        if self.name in instructions:
            # Execute instructions
            if 'what is your name' in instructions or "what's your name" in instructions:
                self.say('My name is ' + self.name)
            elif 'lock' in instructions:
                self.say('As you wish, sir')
                os.system('xscreensaver-command -lock')
            elif 'hello' in instructions:
                self.say('Hello!')


if __name__ == '__main__':
    friday = VoiceAssistant('friday', 'Hello, Boss!')
    while True:
        friday.listen()
