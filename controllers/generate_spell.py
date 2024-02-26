import os
from os import environ
from urllib.parse import urlparse
from dotenv import dotenv_values
from models.monsters import Monsters
from models.hexagons import Hexagons

import re
import json
import openai

env_vars = dotenv_values('.env')
openai.api_key = env_vars["OPENAI_API_KEY"]

key_array = ["Level", "Casting Time", "Range/Area", "Components", "Duration", "School", "Attack/Save", "Damage/Effect"]
key_array = [str(item) for item in key_array]
key_string = ", ".join(key_array)

question_prompt = f"You are a helpful AI assistant that makes the questions for monster content and stat. You can create questions for generating monster content. {key_string}. They are keys that help create the monster's content. If you can know about the key from user's message, you have to ask other keys. And if you know about all keys from user's messages, you don't ask anymore and answer only 'Thanks'."
quiz_sample_message = [
    {
        "role": "system",
        "content": question_prompt
    },
    {
        "role": "user",
        "content": """Hello! I need you to generate questions for monster content and stat. Here's an example: If I give you like that: 'Monster live in forest and have wings', I need you to say : 'Great! We have the environment and appearance covered. Now, could you please let me know the size of the monster? Is it small, medium, or large?'"""
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    },
]


def generate_spell(message_list):
    
    pass