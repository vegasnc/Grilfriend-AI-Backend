import os
from os import environ
from dotenv import dotenv_values
from models.backgrounds import Backgrounds

import re
import json
import openai

env_vars = dotenv_values('.env')
openai.api_key = env_vars["OPENAI_API_KEY"]
COMPLETION_MODEL = env_vars["COMPLETION_MODEL"]
CHAT_COMPLETION_MODEL = env_vars["CHAT_COMPLETION_MODEL"]

background_model = Backgrounds()

question_array = [
    "What is your character's gender?",
    "What are your character’s biggest ambitions?",
    "If you could compare your character to someone in real life that would help others understand them, what would it be?",
    "Why did your character start adventuring?",
    "What is your character’s most prized possession?",
    "What are three things that describe how your character dresses?",
    "If your character could invite any person in the world to a dinner party, living or dead, real or fictional, who would they invite and why?",
    "What are your character’s biggest strengths/weaknesses?",
    "What are your character’s biggest secrets?",
    "What horoscope best describes your character?",
    "What do other people notice first about your character?",
    "What things does your character hate, but will put up with for what he wants/loves most?",
    "What clothing does your character wear?",
    "What are your character’s hobbies or interests?",
    "Is your character a lover or a fighter?",
    "How does your character conduct themselves in public versus when they’re alone with close friends and family? Why this disparity?",
    "Is your character spiritual or religious?",
    "If you could pick one god to be the patron deity of your character, who would it be and why?",
    "Does your character have a family? (living parents, a spouse, children?)",
    "What three smells instantly bring memories of your character to mind?",
    "Is your character a morning person or a night owl?"
]
question_array = [str(item) for item in question_array]
question_string = ", ".join(question_array)

question_prompt = f"You are a helpful AI assistant that makes the questions for backstory of character. You can create questions for generating backstory of character. {question_array}. They are the question templates that help create the backstory. Question templates are just template. So you can change those questions or use this question as it is. If you can know about the character information from user's message, you have to ask other question for getting more information. And if you have about all information from user's messages, or asked all questions from template, you don't ask anymore and answer only 'Thanks'."
quiz_sample_message = [
    {
        "role": "system",
        "content": question_prompt
    },
    {
        "role": "user",
        "content": """Hello! I need you to generate questions for character's backstory. Here's an example: If I give you like that: 'I wanna make attractive and fun backstory', I need you to say : 'Great! Then I have some questions for your character, What are your character’s biggest goal?', Then I will give you like that: 'Explore new lands, discover hidden treasures, and become a legendary adventurer', I need you to say: 'What real-life figure embodies traits similar to your character, aiding in understanding their personality and aspirations?' """
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    },
]

content_prompt = "You are a character backstory generator. Backstory are 1 to 10 paragraphs, you should try to generate 1-3. Backstory have 1 to 2 benefits. Benefits can be Proficiencies, Addition Languages Or Equipment. If you get additional features, you can update the generated backstory. You have to format the backstory content in a homebrewery markdown. If you can't generate the backstory content, answer is empty string."

markdown_sample = """
**Name: Fighter**

**Human, Male**

**Background: ** As a young child, I was enamored with the tales of brave adventurers who traveled far and wide, discovering hidden treasures and exploring uncharted lands. I spent hours poring over maps and listening to the stories of travelers passing through my village, longing for the day when I could set out on my own grand adventure.

One fateful day, I stumbled upon an old map tucked away in the corner of a dusty bookstore. The map depicted unexplored territories, ancient ruins, and untold riches waiting to be discovered. With a newfound sense of purpose burning within me, I set out to follow the map's path and become the legendary adventurer I had always dreamed of being.

***Benefits***
- Proficiency in Cartographer's Tools
- Additional Language: Ancient Script of Lost Civilizations
"""

content_sample_message = [
    {
        "role": "system",
        "content": content_prompt
    },
    {
        "role": "user",
        "content": f"Hello! I need you to generate character's backstory content and return it to me as homebrewery markdown content. Here's an example: If I give you like that: 'I wanna make attractive and fun backstory', I need you to say like that: <background>{markdown_sample}</background>"
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    }
]

start_prompt = "You are a character background content generator. You should create a start prompt for generating character background content of Dungeons & Dragons. Start prompt should be under 10~20 words. Give me a start prompt for generating normal background content."

# Generate background content from user's chat history
def generate_background(message_list, last_content):
    messages = content_sample_message + message_list

    if last_content != "":
        messages[-1]["content"] += "This is last generated background content : " + last_content

    response = openai.ChatCompletion.create(
        model = CHAT_COMPLETION_MODEL,
        messages = messages,
    )

    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]

        pattern = r'<background>(.*?)</background>'
        result = re.search(pattern, assistant_reply, re.DOTALL)
        if result:
            background_item = { "content": result.group(1), "prompt": message_list }
            insert_res = background_model.create(background_item)
            return result.group(1)
        else:
            return ""
    else:
        return "Error"

# Generate question for getting information to generate background content
def generate_question(message_list):
    messages = quiz_sample_message + message_list

    response = openai.ChatCompletion.create(
        model = CHAT_COMPLETION_MODEL,
        messages = messages
    )

    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]

        return assistant_reply
    else:
        return "Error"
    
# Generate background start prompt for background content
def get_background_start_prompt():
    response = openai.Completion.create(model=COMPLETION_MODEL, prompt=start_prompt, max_tokens=20)
    
    if response and response.choices:
        assistant_reply = response.choices[0].text
        return assistant_reply
    pass
