import speech_recognition as sr
import googletrans
  
AUDIO_FILE = ("/home/giulio/Downloads/Audios/audio1.wav")
  
r = sr.Recognizer()
  
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)  
  
try:
    text =  r.recognize_google(audio, language="uk-UA")
    
    print("The audio file contains: " + text)

    # translator = googletrans.Translator()
    # translated = translator.translate(text, src='uk')
    # print("The transcript translates to: " + translated.text)
    
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
  
except sr.RequestError as e:
    print("Could not request results from Google Speech")