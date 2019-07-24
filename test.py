import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    r.adjust_for_ambient_noise(source)
    print('Ready')

    while True:
        # Listen for speech
        try:
            audio = r.listen(source)
            print(r.recognize_google(audio))
        except:
            print("Didn't understand that")
