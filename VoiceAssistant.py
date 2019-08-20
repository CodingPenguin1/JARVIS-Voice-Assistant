import speech_recognition as sr
from os import system
from Command import Command
from subprocess import call
from os import system


class VoiceAssistant:
    def __init__(self, configFilepath):
        self.configFilepath = configFilepath
        self.preferences, self.commands = self.loadConfig()

        for key in self.preferences.keys():
            print(key + ': ' + self.preferences[key])

        self.say(self.preferences['startupQuote'])

    def loadConfig(self):
        # Read config file into list
        lines = []
        file = open(self.configFilepath, 'r')
        for line in file:
            lines.append(line.strip())
        file.close()

        # Declare default preferences
        preferences = {'name': 'Jarvis',
                       'startupQuote': 'At your service, sir',
                       'language': 'en-uk',
                       'pitch': '50',
                       'speed': '160'}

        # Load any custom preferences
        for line in lines:
            # If line has text and isn't a comment, process it
            if len(line) > 0 and line[0] is not '#':
                if line[:line.find('=')] in preferences.keys():
                    preferences[line[:line.find('=')]] = line[line.find('=') + 1:line.find('#')].strip() if line.find('#') != -1 else line[line.find('=') + 1:].strip()

        # Load commands
        commands = {}
        for i, line in enumerate(lines):
            if len(line) > 0 and line[0] == '[':
                commandName = line[1:-1]
                keyphrase = lines[i + 1][lines[i + 1].find('=') + 1:]
                command = lines[i + 2][lines[i + 2].find('=') + 1:]
                response = lines[i + 3][lines[i + 3].find('=') + 1:]
                commands[commandName] = Command(commandName, keyphrase, command, response)

        # for key in list(commands.keys()):
        #     print(commands[key])

        # Return preferences and functions
        return preferences, commands

    def listen(self):
        r = sr.Recognizer()
        mic = sr.Microphone()

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

    def say(self, sentence):
        sentence = sentence.replace('{name}', self.preferences['name'])
        sentence = sentence.replace('{startupQuote}', self.preferences['startupQuote'])
        sentence = sentence.replace('{language}', self.preferences['language'])
        sentence = sentence.replace('{pitch}', self.preferences['pitch'])
        sentence = sentence.replace('{speed}', self.preferences['speed'])
        print('Saying: ' + sentence)
        lang = self.preferences['language']
        s = self.preferences['speed']
        p = self.preferences['pitch']
        system('espeak -v {} -s {} -p {} "{}"'.format(lang, s, p, sentence))

    def act(self, instructions):
        # Make sure the assistant has been summoned:
        if self.preferences['name'].lower() in instructions:
            # Try to find a matching instruction
            for commandName in list(self.commands.keys()):
                command = self.commands[commandName]
                if command.keyphrase in instructions:
                    # Execute command
                    try:
                        if command.executable != 'None':
                            print('Executing: ' + command.executable)
                            try:
                                call(command.executable)
                            except:
                                system(command.executable)
                    except:
                        print('Failed to run: ' + command.executable)
                    # Say response
                    self.say(command.response)


if __name__ == '__main__':
    va = VoiceAssistant('config')
    while True:
        va.listen()
