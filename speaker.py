from os import system

def say(sentence):
    sentence = sentence.replace('{name}', preferences['name'])
    sentence = sentence.replace('{startupQuote}', preferences['startupQuote'])
    sentence = sentence.replace('{language}', preferences['language'])
    sentence = sentence.replace('{pitch}', preferences['pitch'])
    sentence = sentence.replace('{speed}', preferences['speed'])
    print('Saying: ' + sentence)
    lang = preferences['language']
    s = preferences['speed']
    p = preferences['pitch']
    system('espeak -v {} -s {} -p {} "{}"'.format(lang, s, p, sentence))


if __name__ == '__main__':
    preferences = {'name': 'Jarvis',
                   'startupQuote': 'At your service, sir',
                   'language': 'en-uk',
                   'pitch': '50',
                   'speed': '160'}
    say()