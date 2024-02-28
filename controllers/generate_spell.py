import os
from os import environ
from urllib.parse import urlparse
from dotenv import dotenv_values
from models.spells import Spells

import re
import json
import openai

env_vars = dotenv_values('.env')
openai.api_key = env_vars["OPENAI_API_KEY"]
COMPLETION_MODEL = env_vars["COMPLETION_MODEL"]
CHAT_COMPLETION_MODEL = env_vars["CHAT_COMPLETION_MODEL"]

spell_model = Spells()

question_array = ["What level of spell would you like? (If unspecified, I can default to a certain level.)",
                 "Can you describe the main effect or purpose of the spell?",
                 "How quickly would you like the spell to be cast? (e.g., instantaneously, within 1 action, over a period of time)",
                 "Who or what is the target or affected area of the spell? (e.g., self, creature, area of effect)",
                 "Are there any specific components required to cast the spell?",
                 "How long do you want the spell's effects to last?",
                 "Would you like the spell to deal damage, provide a benefit, or have another effect?",
                 "Is there a particular theme or school of magic you'd like the spell to belong to?",
                 "Any additional details or flavor you'd like to add about the spell?"]
question_array = [str(item) for item in question_array]
question_string = ", ".join(question_array)

question_prompt = f"You are a helpful AI assistant that makes the questions for spell. You can create questions for generating spell. {question_array}. They are the sample questions that help create the spell. If you can know about the spell information from user's message, you have to ask other question for getting more information. And if you know about all information from user's messages, you don't ask anymore and answer only 'Thanks'."
quiz_sample_message = [
    {
        "role": "system",
        "content": question_prompt
    },
    {
        "role": "user",
        "content": """Hello! I need you to generate questions for spell. Here's an example: If I give you like that: 'Spell name is Blazing Shield.', I need you to say : 'Great! We have the spell name. Now, What level of spell would you like?', Then I will give you like that: 'Level is 2nd', I need you to say: 'Can you describe the main effect or purpose of the spell?' """
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    },
]

content_prompt = "You are a spell generator. You can create spell name, level, casting time, range/area, components, duration, school, attack/save, damage/effect and description. You should include the 'Description'  section. If you get additional features, you can update the spell features and description. You have to format the spell content in a homebrewery markdown. If you can't generate the spell content, answer is empty string."

markdown_sample = """
**Spell Name:** Arcane Distortion

**Level:** 3rd level

**Main Effect/Purpose:** This spell distorts the fabric of arcane energy, disrupting magical effects in the area.

**Casting Time:** 1 action

**Target/Affected Area:** 20-foot radius sphere centered on a point within range

**Components:** Verbal, Somatic

**Duration:** Instantaneous

**School:** Abjuration

**Description:** You unleash a surge of chaotic arcane energy at a point you can see within range. Each creature within a 20-foot radius sphere centered on that point must make an Intelligence saving throw. On a failed save, a creature's concentration on a spell is broken, and any ongoing magical effects within the area are temporarily suppressed for 1d4 rounds.

**At Higher Levels:** When you cast this spell using a spell slot of 4th level or higher, the radius of the area increases by 5 feet for each slot level above 3rd.

**Additional Details/Flavor:** Arcane energy crackles and warps in the affected area, causing disturbances in spells and magical effects. The air feels charged with energy, and spellcasters may experience a momentary disorientation as their magical connections falter.

This spell is particularly useful for disrupting enemy spellcasters' concentration and temporarily neutralizing ongoing magical effects in a given area, making it valuable in both offensive and defensive situations. However, its effectiveness may vary depending on the targets' intelligence and their reliance on magic.
"""

content_sample_message = [
    {
        "role": "system",
        "content": content_prompt
    },
    {
        "role": "user",
        "content": f"Hello! I need you to generate spell content and return it to me as homebrewery markdown content. Here's an example: If I give you like that: 'Level is 3', I need you to say like that: <spell>{markdown_sample}</spell>"
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    }
]

start_prompt = "You are a spell content generator. You should create a start prompt for generating spell content of Dungeons & Dragons. Start prompt should be under 10~20 words. Give me a start prompt for generating spell content"

# Generate Spell content from user's chat history
def generate_spell(message_list, last_content):
    messages = content_sample_message + message_list

    if last_content != "":
        messages[-1]["content"] += "This is last generated spell content : " + last_content

    response = openai.ChatCompletion.create(
        model = CHAT_COMPLETION_MODEL,
        messages = messages,
    )

    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]

        pattern = r'<spell>(.*?)</spell>'
        result = re.search(pattern, assistant_reply, re.DOTALL)
        if result:
            spell_item = { "content": result.group(1), "prompt": message_list }
            insert_res = spell_model.create(spell_item)
            return result.group(1)
        else:
            return ""
    else:
        return "Error"

# Generate question for getting information to generate spell content
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
    
# Generate spell start prompt for spell content
def get_spell_start_prompt():
    response = openai.Completion.create(model=COMPLETION_MODEL, prompt=start_prompt, max_tokens=20)
    print(f"{response}")
    
    if response and response.choices:
        assistant_reply = response.choices[0].text
        return assistant_reply
    pass
