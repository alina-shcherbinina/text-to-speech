# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 17:14:57 2020

@author: Alina Shcherbinina
"""
import io
import requests
from langdetect import detect
from pydub import AudioSegment
import soundfile as sf


def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

def tts(text):
    # get token

    auth_url = "https://francecentral.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    key = "be5f4c47488e4d349dbb06b527492c7c" 

    auth_headers = { 
        "Ocp-Apim-Subscription-Key": key, 
        "Content-Length": "0", 
        "Content-type": "application/x-www-form-urlencoded" 
        }
    
    auth_response = requests.post(auth_url, headers=auth_headers)
    token = auth_response.text #thats a bearer 
    
    print("'\n'token/bearer in use: ", token,'\n')
    
    # get voice list
    
    lang_url = "https://francecentral.tts.speech.microsoft.com/cognitiveservices/voices/list"
    
    lang_headers= { 
        "Authorization": "Bearer " + token,
        }
    
    lang_response = requests.get(lang_url, headers=lang_headers)
    json_langs = lang_response.json()
    
    # choose the right one somehow 
    
    print("Language of a given text: ", detect(full_text), '\n')
    
    lang_of_text = detect(full_text)
    
    for voice in json_langs:
        locale = json_extract(voice,'Locale')
        locale = ''.join(locale)
        if (locale.find(lang_of_text) != -1):
            index = json_langs.index(voice)
    
    
    needed_voice = json_langs[index]
    
    print("The following file will be read to you by: ", needed_voice,'\n')
    
    api_url = "https://francecentral.tts.speech.microsoft.com/cognitiveservices/v1"
    
    api_headers = {
        "Authorization": "Bearer " + token,
        "X-Microsoft-OutputFormat": "raw-16khz-16bit-mono-pcm",
        "Content-Type": "application/ssml+xml"
        }
    
    # make data about all that in xml 
    
    lang = json_extract(needed_voice, 'Locale')
    lang = ''.join(lang)
    gender = json_extract(needed_voice, 'Gender')
    gender = ''.join(gender)
    name = json_extract(needed_voice, 'ShortName')
    name = ''.join(name)
    
    
    final_xml = "<speak version='1.0' xml:lang='" + lang + "'><voice xml:lang='" + lang + "' xml:gender='" + gender + "' name='" + name + "'>" + full_text + "</voice></speak>"
    
    
    # make a request to api. response is binary; file is in mp3 or whatever
    
    request = requests.post(api_url, headers = api_headers, data = final_xml)
    response = request.content
    
    wav_file = user_file + ".wav"
    
    s = io.BytesIO(response)
    frame = json_extract(needed_voice, 'SampleRateHertz')
    frame = ''.join(frame)
    audio = AudioSegment.from_raw(s, sample_width = 2, frame_rate = int(frame), channels = 1).export(wav_file, format = 'wav')
    print("Generated .wav file! -- > ", wav_file,'\n')
    
    # additional work
    
    #print(len(full_text))
    f = sf.SoundFile(wav_file)
    sec = format(len(f) / f.samplerate)
    #print(sec)
    
    result =  float(sec) / len(full_text)
    
    print("Seconds per symbol: ", result,'\n')
    
    
# my vars

full_text = ""


# ask a name of a text file to read

print(" ~ text to speech! ~ ")

user_file = input('input! Choose file to read (ex.: text): ')
user_file1 = user_file + ".txt"
try:
    file_in = open(user_file1, "r", encoding="utf-8") 
    for line in file_in:
        full_text +=line
    tts(full_text)
except:
    print("\nSomething went wrong with the file")

print('\n'" ~ end of program ~ ")



