import json
import toml
import os
import aiofiles
import httpx
import asyncio

if (not os.path.exists("azure_secret.json")):
    with open("azure_secret.json", "w+") as f:
        json.dump({"key": "", "region": ""}, f, indent=3)
    print("Please enter your key and region in azure_secret.json")
    exit(1)

try:
    with open("azure_secret.json") as f:
        azure_secret_key = json.load(f)
        azure_speech_key = azure_secret_key["key"]
        azure_speech_region = azure_secret_key["region"]
except:
    print("Could not load azure_secret.json. Please enter your key and region in azure_secret.json")
    exit(1)

if (not os.path.exists("output")):
    os.mkdir("output")

SSML = """
<speak version='1.0' xml:lang='{language_code}'>
    <voice xml:lang='{language_code}' name='{voice_name}' style='{style}'>
        <prosody pitch='{pitch}%' rate='{speed}%'>
            {text}
        </prosody>
    </voice>
</speak>
"""

# Simpler
# SSML = """
# <speak version='1.0' xml:lang='{language_code}'>
#     <voice xml:lang='{language_code}' name='{voice_name}'>
#         {text}
#     </voice>
# </speak>
# """


def to_speech(text: str, *, language_code: str, voice_name: str, speed: float, pitch: float, style: str = None) -> bytes:
    style = style or 'neutral'
    response = httpx.post("https://westeurope.tts.speech.microsoft.com/cognitiveservices/v1",
                          headers={"Ocp-Apim-Subscription-Key": azure_speech_key,
                                   "Content-Type": "application/ssml+xml",
                                   "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
                                   "User-Agent": "shorts"},

                          data=SSML.format(text=text, language_code=language_code, voice_name=voice_name, speed=speed, pitch=pitch, style=style).encode("utf-8"))  # Encode to utf-8 for all the special characters
    return response.content


async def create_speech_file(filename: str, text: str, *, language_code: str, voice_name: str, pitch: float, speed: float, style: str = None):
    style = style or 'neutral'
    async with httpx.AsyncClient() as client:
        response = await client.post("https://westeurope.tts.speech.microsoft.com/cognitiveservices/v1",
                                     headers={"Ocp-Apim-Subscription-Key": azure_speech_key,
                                              "Content-Type": "application/ssml+xml",
                                              "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
                                              "User-Agent": "shorts"},
                                     data=SSML.format(text=text, language_code=language_code, voice_name=voice_name, pitch=pitch, speed=speed, style=style).encode("utf-8"))  # Encode to utf-8 for all the special characters
        speech = response.content
        if (not speech):
            raise RuntimeError(f"No data returned from azure. Status: {response.status_code}")
        print(f"Writing {filename}.wav")
        async with aiofiles.open(f"output/{filename}.wav", "wb+") as f:
            await f.write(speech)

import re
valid_name = re.compile(r"^[a-zA-Z0-9_\-]+$")

def main():
    futures = []
    with open("speech.toml") as f:
        texts = toml.load(f)
        for filename, tts_data in texts.items():
            text = tts_data.get("text", None)
            voice_name = tts_data.get("voice", None)
            language_code = tts_data.get("language", None)
            pitch = float(tts_data.get("pitch", 1.0))
            speed = float(tts_data.get("speed", 1.0))
            style = tts_data.get("style", 'neutral')
            # Check if the file name is safe
            if not valid_name.match(filename):
                print(f"Skipping {filename} because it is not a valid file name")
                continue
            if not text:
                print(f"Skipping {filename} because no text was found")
                continue
            if not language_code:
                print(f"Skipping {filename} because no language code was found")
                continue
            # print(SSML.format(text=text, language_code=language_code, voice_name=voice_name, speed=speed, pitch=pitch))
            # continue
            futures.append(
                asyncio.ensure_future(
                    create_speech_file(filename, text, language_code=language_code, voice_name=voice_name, pitch=pitch, speed=speed, style=style)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*futures))


if __name__ == "__main__":
    main()


def get_voice_list():
    r = httpx.get(f"https://{azure_speech_region}.tts.speech.microsoft.com/cognitiveservices/voices/list",
                  headers={"Ocp-Apim-Subscription-Key": azure_speech_key})
    return r.json()


def listvoices():
    voices = get_voice_list()
    with open("voices.json", "w") as f:
        json.dump(voices, f, indent=3)
    print("Voices written to voices.json")


def output2ogg():
    os.system("cd output && for f in *.wav; do ffmpeg -i \"$f\" -acodec libvorbis \"${f%.wav}.ogg\"; done")

def output2mp3():
    os.system("cd output && for f in *.wav; do ffmpeg -i \"$f\" -acodec libmp3lame \"${f%.wav}.mp3\"; done")


def cleanwav():
    os.system("cd output ; rm -v *.wav")


def cleanogg():
    os.system("cd output ; rm -v *.ogg")

def cleanmp3():
    os.system("cd output ; rm -v *.mp3")


def clean():
    """Cleans the output folder"""
    cleanogg()
    cleanwav()
    cleanmp3()


def generate():
    """Generates the speech files"""
    main()
    output2ogg()
    output2mp3()
    cleanwav()
