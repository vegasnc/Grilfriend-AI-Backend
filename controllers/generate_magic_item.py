import os
from os import environ
from dotenv import dotenv_values
from models.magicitems import Magicitems

import re
import json
import openai

env_vars = dotenv_values('.env')
openai.api_key = env_vars["OPENAI_API_KEY"]
COMPLETION_MODEL = env_vars["COMPLETION_MODEL"]
CHAT_COMPLETION_MODEL = env_vars["CHAT_COMPLETION_MODEL"]

magicitem_model = Magicitems()

question_array = [
    "What does the item look like? Describe how it appears, such as its shape, color, and any special decorations.",
    "What can the item do? Explain the special powers or abilities the item has, like making someone invisible or shooting sparks.",
    "Are there any rules for using it? Discuss any limits or conditions for using the item, like needing to say a magic word or only working at night.",
    "Is there anything tricky about the item? Talk about any downsides or challenges of using the item, such as it being too heavy or needing special care.",
    "How rare and important is the item? Explain if it's a common item or a super rare one, and why it's valuable in the game world.",
    "Does the item have a story or history? Share any cool stories about how the item was made or used by heroes in the past.",
    "Can the item get stronger? Discuss if the item can grow more powerful over time or gain new abilities as players use it more.",
    "What is the item's purpose? Explain why the item exists and how it helps players in their adventures, like protecting them from danger or helping them find treasure."
]
question_array = [str(item) for item in question_array]
question_string = ", ".join(question_array)

question_prompt = f"You are a helpful AI assistant that makes the questions for generating magic items of D&D game. You can create questions for generating magic items. {question_array}. That are the sample questions that help create the magic items. Sample question are just sample. So you can change those questions or use this question as it is. But you should ask a question one by one. If you can know about information of magic item information from user's message, you have to ask other question for getting more information. And if you have about all information from user's messages, or asked all questions from template, you don't ask anymore and answer only 'Thanks'."
quiz_sample_message = [
    {
        "role": "system",
        "content": question_prompt
    },
    {
        "role": "user",
        "content": """Hello! I need you to generate questions for magic items. Here's an example: If I give you like that: 'I wanna make wonderful magic item', I need you to say : 'Great! Then I have some questions for your magic item, What does the item look like? Describe how it appears, such as its shape, color, and any special decorations.', Then I will give you like that: 'The item is a silver crescent pendant with sapphire gems and a starburst engraving, looking mystical and celestial', I need you to say: 'What can the item do? Explain the special powers or abilities the item has, like making someone invisible or shooting sparks.' """
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    },
]

markdown_sample = """
**Name: Celestial Starburst Amulet**

**Amulet, uncommon (requires attunement)**

This silver crescent pendant with sapphire gems and a starburst engraving grants the following abilities:

- **Lunar Blessing:** Once per day, the wearer can gain advantage on a saving throw against dark magic or attacks during nighttime.

- **Stellar Guidance:** As an action, the wearer can summon a guiding star to illuminate dark areas or reveal hidden paths. This effect lasts for 1 hour and can be used once per long rest.

The amulet also serves as a stylish accessory when not in use for its magical properties.

**Notes: Lunar Protection, Starlight Guidance**

**Item Tags: PROTECTION, GUIDANCE**
"""

content_prompt = f"""You are a D&D game magic item generator. Those are 7 tips for creating custom magic items.
1. Take inspiration from existing magic items.
2. Tailor items specifically for characters.
3. Make items that are part of the world's lore.
4. Help characters with their weaknesses.
5. Empower Your Characters' Strengths.
6. Make Items That Get More Powerful As Characters Level Up.
7. Add Risk And Reward By Creating Cursed Items
You should reference those tips for generating new magic items.
If you get additional features, you can update the generated magic item. You have to format the magic item content in a homebrewery markdown. Even if the provided information is limited, you should interpret the user's intention and create the content accordingly. Your generated content must be enclosed between <magicitem> and </magicitem>. For example: If the user provides like that: 'The item is a silver crescent pendant with sapphire gems and a starburst engraving, looking mystical and celestial', your response should be like that: '<magicitem>{markdown_sample}</magicitem>'. And if the user wants multiple items, you should generate multiple items. Like this example, you should re-generate only related parts from the last content and continue this format for subsequent requests, ensuring <magicitem> tag are included in the generated response."""

content_sample_message = [
    {
        "role": "system",
        "content": content_prompt
    },
    {
        "role": "user",
        "content": f"Hello! I need you to generate magic items and return it to me as homebrewery markdown content. Here's an example: If I give you like that: 'The item is a silver crescent pendant with sapphire gems and a starburst engraving, looking mystical and celestial', I need you to say like that: <magicitem>{markdown_sample}</magicitem>"
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    }
]

start_prompt = "You are a D&D magic item generator. You should create a start prompt for generating magic item of Dungeons & Dragons. Start prompt should be under 10~20 words. Give me a start prompt for generating normal magic item."

# Generate magic item content from user's chat history
def generate_magic_item(message_list, last_content):
    messages = content_sample_message + message_list

    if last_content != "":
        messages[-1]["content"] += "This is last generated magic item : " + last_content

    response = openai.ChatCompletion.create(
        model = CHAT_COMPLETION_MODEL,
        messages = messages,
    )

    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]

        pattern = r'<magicitem>(.*?)</magicitem>'
        results = re.findall(pattern, assistant_reply, re.DOTALL)
        if results:
            contents = ""
            for item in results:
                contents += item + " ### "
            magic_item_item = { "content": contents, "prompt": message_list }
            insert_res = magicitem_model.create(magic_item_item)
            return contents
        else:
            return ""
    else:
        return "Error"

# Generate question for getting information to generate magic item content
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
    
# Generate magic item start prompt for magic item content
def get_magic_item_start_prompt():
    response = openai.Completion.create(model=COMPLETION_MODEL, prompt=start_prompt, max_tokens=20)
    
    if response and response.choices:
        assistant_reply = response.choices[0].text
        return assistant_reply
    pass
