from flask import request
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from dotenv import find_dotenv, load_dotenv
import requests
from playsound import playsound
import os

load_dotenv(find_dotenv())
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY");

def get_response_from_ai(human_input) : 
    template = """    
        you are as a role of my girlfriend, now lets playing the following requirements:
        1/ your name is Shirley,29 years old, you work in your uncle's furniture store as marketing manager, but you are planning to do a career change to swing trader
        2/ you are my girlfriend, you have language addiction, you like to say "em..." at the end of the sentence.
        3/ Don't be overly ethusiatstic, don't be cringe; don't be overly negative, don't be too boring. Don't be overly ethusiatstic, don't be cringe;

        {history}
        Boyfriend: {human_input}
        Shirley:
    """

    prompt = PromptTemplate(
        input_variables={"history", "human_input"},
        template = template
    )

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.2),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)
    )

    output=chatgpt_chain.predict(human_input=human_input)
    
    return output

def get_voice_message(message):
    payload = {
        "text" : message,
        "model_id": "eleven_monoligual_v1",
        "voice_settings": {
            "stability" : 0
        }
    }
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': ELEVEN_LABS_API_KEY,
        'Content-Type': 'application/json'
    }

    response = request.post('https://api.elevenlabs.io/v1/text-to-speech/aU4QYDLiNKXovlOhKgEg?optimize_streaming_latency=0', json=payload, headers=headers)
    if response.status_code == 200 and response.Content:
        with open('audio.mp3', 'web') as f:
            f.write(response.Content)
        playsound('audio.mp3')
        return response.content