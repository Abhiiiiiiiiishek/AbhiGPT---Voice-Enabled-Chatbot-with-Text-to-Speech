import asyncio
import concurrent.futures
import logging
import os
import speech_recognition as sr
import simpleaudio as sa
from gtts import gTTS
from pydub import AudioSegment
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# Set OpenAI API key
openai.api_key = "Enter your api key"

# Executor for running blocking tasks
executor = concurrent.futures.ThreadPoolExecutor()

async def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Error communicating with OpenAI API: %s", e)
        return None

async def process_audio(recognized_text):
    try:
        response = await chat_with_gpt("You: " + recognized_text)
        if response:
            logger.info("AbhiGPT: %s", response)
            tts_text = "AbhiGPT!: " + response
            language = 'en'
            tts = gTTS(text=tts_text, lang=language, slow=False)
            tts.save("latest.mp3")

            sound = AudioSegment.from_mp3("latest.mp3")
            sound.export("latest.wav", format="wav")

            # Play audio asynchronously
            await play_audio("latest.wav")

    except Exception as e:
        logger.error("Error processing audio: %s", e)

async def play_audio(audio_file):
    try:
        wave_obj = sa.WaveObject.from_wave_file(audio_file)
        play_obj = wave_obj.play()
        await asyncio.get_event_loop().run_in_executor(executor, play_obj.wait_done)
    except Exception as e:
        logger.error("Error playing audio: %s", e)

async def listen_microphone():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            logger.info("Kindly voice out your command!")
            audio = r.listen(source)

        try:
            recognized_text = r.recognize_google(audio)
            if 'hello' in recognized_text.lower():
                await asyncio.gather(process_audio("hello"))
            else:
                logger.warning("Sorry, I could not understand your command.")

        except sr.UnknownValueError:
            logger.warning("Sorry, I could not understand your command.")
        except sr.RequestError as e:
            logger.error("Error fetching results: %s", e)

async def main():
    await asyncio.gather(listen_microphone())

if _name_ == "_main_":
    asyncio.run(main())
