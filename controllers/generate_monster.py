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
COMPLETION_MODEL = env_vars["COMPLETION_MODEL"]
CHAT_COMPLETION_MODEL = env_vars["CHAT_COMPLETION_MODEL"]

monster_model = Monsters()
hexagon_model = Hexagons()
        
key_array = ["Environment", "Size", "Appearance", "Attack Mode", "Movement Speed"]
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

markdown_sample = """
## Abyssal Wing

*Large fiend, chaotic evil*

---

###

- **Armor Class** 18 (natural armor)
- **Hit Points** 189 (18d10 + 90)
- **Speed** 40 ft., fly 60 ft., swim 40 ft.

---

###

|STR|DEX|CON|INT|WIS|CHA|
|-|-|-|-|-|-|
|21 (+5)|16 (+3)|20 (+5)|14 (+2)|15 (+2)|18 (+4)|

---

###

- **Skills** Perception +6, Stealth +8
- **Damage Resistances** cold, fire, lightning; bludgeoning, piercing, and slashing from nonmagical attacks
- **Damage Immunities** poison
- **Condition Immunities** poisoned
- **Senses** darkvision 120 ft., passive Perception 16
- **Languages** Abyssal, Aquan
- **Challenge** 14 (11,500 XP)

---

###

***Amphibious.*** The abyssal wing can breathe air and water.

***Innate Spellcasting.*** The abyssal wing's innate spellcasting ability is Charisma (spell save DC 16). It can innately cast the following spells, requiring no material components:

- At will: *darkness, fog cloud*
- 3/day each: *invisibility, water breathing*
- 1/day each: *control water, teleport*

***Echolocation.*** The abyssal wing can't be blinded or deafened, and it has blindsight with a radius of 60 feet.

***Shadow Step.*** The abyssal wing can magically teleport up to 120 feet to an unoccupied space it can see that is also in darkness.

***Regeneration.*** The abyssal wing regains 10 hit points at the start of its turn if it has at least 1 hit point.

---

### Actions

***Multiattack.*** The abyssal wing makes three attacks: one with its *bite* and two with its *claws*.

***Bite.*** *Melee Weapon Attack:* +9 to hit, reach 10 ft., one target. *Hit:* 16 (2d10 + 5) piercing damage plus 7 (2d6) poison damage.

***Claw.*** *Melee Weapon Attack:* +9 to hit, reach 5 ft., one target. *Hit:* 14 (2d8 + 5) slashing damage.

---

### Legendary Actions

The abyssal wing can take 3 legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The abyssal wing regains spent legendary actions at the start of its turn.

- **Move.** The abyssal wing moves up to half its flying or swimming speed.
- **Make a Bite Attack.** The abyssal wing makes a bite attack.
- **Make a Dark Mist (Costs 2 Actions).** The abyssal wing releases a cloud of dark mist in a 20-foot radius centered on itself. The mist spreads around corners, and its area is heavily obscured. Each creature that starts its turn in the mist must make a DC 16 Wisdom saving throw or be frightened until the end of its next turn.
"""

updated_markdown_sample = """
## Abyssal Wing (Small)

*Small fiend, chaotic evil*

---

### 

- **Armor Class** 18 (natural armor)
- **Hit Points** 189 (18d10 + 90)
- **Speed** 30 ft., fly 40 ft., swim 30 ft.

---

### 

|STR|DEX|CON|INT|WIS|CHA|
|-|-|-|-|-|-|
|11 (+0)|16 (+3)|20 (+5)|14 (+2)|15 (+2)|18 (+4)|

---

### 

- **Skills** Perception +6, Stealth +5
- **Damage Resistances** cold, fire, lightning; bludgeoning, piercing, and slashing from nonmagical attacks
- **Damage Immunities** poison
- **Condition Immunities** poisoned
- **Senses** darkvision 120 ft., passive Perception 16
- **Languages** Abyssal, Aquan
- **Challenge** 14 (11,500 XP)

---

### 

***Amphibious.*** The abyssal wing can breathe air and water.

***Innate Spellcasting.*** The abyssal wing's innate spellcasting ability is Charisma (spell save DC 16). It can innately cast the following spells, requiring no material components:

- At will: *darkness, fog cloud*
- 3/day each: *invisibility, water breathing*
- 1/day each: *control water, teleport*

***Echolocation.*** The abyssal wing can't be blinded or deafened, and it has blindsight with a radius of 60 feet.

***Shadow Step.*** The abyssal wing can magically teleport up to 60 feet to an unoccupied space it can see that is also in darkness.

***Regeneration.*** The abyssal wing regains 10 hit points at the start of its turn if it has at least 1 hit point.

---

### Actions

***Multiattack.*** The abyssal wing makes three attacks: one with its *bite* and two with its *claws*.

***Bite.*** *Melee Weapon Attack:* +5 to hit, reach 5 ft., one target. *Hit:* 7 (1d10 + 2) piercing damage plus 3 (1d6) poison damage.

***Claw.*** *Melee Weapon Attack:* +5 to hit, reach 5 ft., one target. *Hit:* 6 (1d6 + 3) slashing damage.

---

### Legendary Actions

The abyssal wing can take 3 legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The abyssal wing regains spent legendary actions at the start of its turn.

- **Move.** The abyssal wing moves up to half its flying or swimming speed.
- **Make a Bite Attack.** The abyssal wing makes a bite attack.
- **Make a Dark Mist (Costs 2 Actions).** The abyssal wing releases a cloud of dark mist in a 10-foot radius centered on itself. The mist spreads around corners, and its area is heavily obscured. Each creature that starts its turn in the mist must make a DC 16 Wisdom saving throw or be frightened until the end of its next turn.
"""

dalle3_prompt = """Create an eerie depiction of a Abyssal Wing emerging from the deplths of a dense, ancient forest, its form blending seamlessly with the shadows and twisted foliage around it. Capture the sense of malevelence and stealth as it perpares to unleash its claws and shadowy powers upon unsuspecting adventurers."""

content_prompt = "You are a D&D monster content generator specialized in creating descriptions and stat blocks. Your task is to generate compelling monster descriptions with accompanying stat blocks and challenge ratings. Each description should include the stat and ability block and challenge rating. Additionally, there should be an 'Action' section, but a 'Legendary Actions' section is only created if the user requests it. For abilities, use abbreviated terms such as 'Str' for 'Strength' and 'Dex' for 'Dexterity'. When generating the monster content, ensure it is formatted in Homebrewery markdown. Even if the provided monster information is limited, you should interpret the user's intention and create the content accordingly. If the user requests a new monster, update all elements from the monster name onwards to completely different words, ensuring uniqueness and attractiveness. Do not use repeated words within one monster's content. And if the user wants multiple monsters, you should generate multiple monsters. In this case, you should generate the DALLE3 prompt for each generated monsters. Your generated monster content must be enclosed between <monster> and </monster>, and the corresponding DALLE3 prompt should be enclosed between <dalle> and </dalle>. Here's an example: If the user provides like that: 'Monster live in forest', your response should be like this: '<monster> {markdown_sample} </monster> \n <dalle> {dalle3_prompt} </dalle>'. Continue, If the user provides like that : 'red eye and too small.', your response should be like that: '<monster> {updated_markdown_sample} </monster> \n <dalle> {dalle3_prompt} </dalle>'. Like this example, you should re-generate only related parts from the last content and continue this format for subsequent requests, ensuring both <monster> and <dalle> tags are included in the generated response."

content_sample_message = [
    {
        "role": "system",
        "content": content_prompt
    },
    {
        "role": "user",
        "content": """
            Here's an example: If I give you like that: 'Monster live in forest', I need you to say like that: '<monster> {markdown_sample} </monster> \n <dalle> {dalle3_prompt} </dalle>'. Continue, If I give you like that : 'red eye and too small.', I need you to say like that: '<monster> {updated_markdown_sample} </monster> \n <dalle> {dalle3_prompt} </dalle>'. Like this example, you should re-generate only related parts from last content.
        """
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    }
]

start_prompt = "You are a monster content generator. You should create a start prompt for generating monster content of Dungeons & Dragons. Start prompt should be under 10~20 words. Don't specify the monster's features like monster name and so on. Give me a start prompt for generating monster content"

# Generate Monster content from user's chat history
def generate_content(message_list, last_content):
    messages = content_sample_message + message_list

    if last_content != "":
        messages[-1]["content"] += "\n This is last generated monster content : " + last_content

    response = openai.ChatCompletion.create(
        model = CHAT_COMPLETION_MODEL,
        messages = messages,
    )

    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]

        print(f"----- {  assistant_reply }")

        monster_pattern = r'<monster>(.*?)</monster>'
        dalle_pattern = r'<dalle>(.*?)</dalle>'
        results = re.findall(monster_pattern, assistant_reply, re.DOTALL)
        if results:
            contents = ""
            for item in results:
                contents += item + " ### "
            monster_item = { "content": contents, "prompt": message_list, "dalle_prompt": "" }
            insert_res = monster_model.create(monster_item)
            return contents, ""
            # # Get dalle3 prompt for generated monster content
            # prompt = ""
            # dalle_result = re.search(dalle_pattern, assistant_reply, re.DOTALL)
            # if dalle_result:
            #     prompt = dalle_result.group(1)

            # monster_item = { "content": result.group(1), "prompt": message_list, "dalle_prompt": prompt }
            # insert_res = monster_model.create(monster_item)
            # return result.group(1), prompt
        else:
            return "", ""
    else:
        return "Error", ""

# Generate question for getting information to generate monster content
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
    
# Save generated monster content
def save_updated_content(message_list, updated_content):
    monster_item = { "content": updated_content, "prompt": message_list }
    inserted_id = monster_model.create(monster_item)

    if inserted_id:
        return True
    return False

# Get generated hexagon items
def get_hexagon_data():
    hexagon_data = hexagon_model.find({})
    return hexagon_data

# Generate hexagon item from openai
def create_hexagon_Data():
    data = [
        {
            "color": "#CFC38F",
            "img_url": "/images/chat_dashboard.png"
        },
        {
            "color": "#AC2AB8",
            "img_url": "/images/chat_dashboard.png"
        },
        {
            "color": "#442846",
            "img_url": "/images/chat_dashboard.png"
        },
        {
            "color": "#D8A539",
            "img_url": "/images/chat_dashboard.png"
        },
        {
            "color": "#82A2C9",
            "img_url": "/images/chat_dashboard.png"
        },
        {
            "color": "#CFC38F",
            "img_url": "/images/chat_dashboard.png"
        },
        {
            "color": "#442846",
            "img_url": "/images/chat_dashboard.png"
        }
    ]

    for item in data:
        res = hexagon_model.create(item)

    return True
        
# Generate monster start prompt for monster content
def get_monster_start_prompt():
    response = openai.Completion.create(model=COMPLETION_MODEL, prompt=start_prompt, max_tokens=20)
    
    if response and response.choices:
        assistant_reply = response.choices[0].text
        return assistant_reply
    return ""

