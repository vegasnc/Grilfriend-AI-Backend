import os
from os import environ
from urllib.parse import urlparse
from dotenv import dotenv_values
from models.npcs import Npcs
from models.hexagons import Hexagons

import re
import json
import openai

env_vars = dotenv_values('.env')
openai.api_key = env_vars["OPENAI_API_KEY"]
COMPLETION_MODEL = env_vars["COMPLETION_MODEL"]
CHAT_COMPLETION_MODEL = env_vars["CHAT_COMPLETION_MODEL"]

npc_model = Npcs()
hexagon_model = Hexagons()
        
key_array = ["Environment", "Size", "Appearance", "Attack Mode", "Movement Speed"]
key_array = [str(item) for item in key_array]
key_string = ", ".join(key_array)

question_prompt = f"You are a helpful AI assistant that makes the questions for NPC content. You can create questions for generating NPC content. {key_string}. They are keys that help create the NPC's content. If you can know about the key from user's message, you have to ask other keys. And if you know about all keys from user's messages, you don't ask anymore and answer only 'Thanks'."
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
## Forest Guardian

*Large fey, neutral*

---

###

- **Armor Class** 17 (natural armor)
- **Hit Points** 136 (13d10 + 65)
- **Speed** 40 ft.

---

###

|STR|DEX|CON|INT|WIS|CHA|
|-|-|-|-|-|-|
|20 (+5)|16 (+3)|20 (+5)|14 (+2)|18 (+4)|16 (+3)|

---

###

- **Skills** Perception +8, Stealth +6
- **Damage Resistances** bludgeoning, piercing, and slashing damage from nonmagical attacks
- **Damage Immunities** poison
- **Condition Immunities** poisoned
- **Senses** darkvision 60 ft., passive Perception 18
- **Languages** Sylvan, Elvish
- **Challenge** 9 (5,000 XP)

---

###

***Innate Spellcasting.*** The forest guardian's innate spellcasting ability is Wisdom (spell save DC 16). It can innately cast the following spells, requiring no material components:

- At will: *druidcraft, entangle, pass without trace*
- 3/day each: *call lightning, barkskin*
- 1/day: *plant growth*

***Tree Stride.*** Once on its turn, the forest guardian can use 10 feet of its movement to step magically into one living tree within its reach and emerge from a second living tree within 60 feet of the first tree, appearing in an unoccupied space within 5 feet of the second tree. Both trees must be Large or bigger.

***Regeneration.*** The forest guardian regains 10 hit points at the start of its turn if it has at least 1 hit point.

***Spellbreaker.*** The forest guardian has advantage on saving throws against spells and other magical effects.

***Race:*** Elf
***Class:*** Ranger
***Alignment:*** Neutral Good
***Age:*** 120 years
***Height:*** 5'8"
***Eyes:*** Emerald green
***Hair:*** Long silver hair

---

###

***Personality:*** Forest Guardian is quiet and observant, preferring the company of nature over bustling cities. She is fiercely protective of the forest and its inhabitants, often seen as a guardian by the woodland creatures. Despite her reserved nature, she is kind-hearted and willing to aid those in need.

***Backstory:*** Born under the canopy of ancient trees, Forest Guardian learned the ways of the forest from her elven kin. She honed her skills as a ranger, mastering archery and survival in the wilderness. Forest Guardian's bond with nature runs deep, and she feels a responsibility to preserve the balance of the natural world.

***Goals:***
- Protect the ancient forest from threats.
- Uncover the source of corruption creeping into the woods.
- Aid adventurers who show respect for nature and its creatures.

***Interactions:***
- Offers guidance and advice to adventurers navigating the forest.
- Provides quests related to protecting wildlife, investigating strange occurrences, or dealing with hostile forces threatening the forest.
- Trades rare herbs, potions, and enchanted items made from natural materials.

***Notes:*** Forest Guardian can be a valuable ally to adventurers who share her reverence for nature. Building a positive relationship with her may unlock hidden knowledge about the forest's secrets or grant access to powerful nature-based abilities.

---

### Actions

***Multiattack.*** The forest guardian makes two attacks: one with its *wooden club* and one with its *thorny vine whip*.

***Wooden Club.*** *Melee Weapon Attack:* +9 to hit, reach 10 ft., one target. *Hit:* 14 (2d8 + 5) bludgeoning damage.

***Thorny Vine Whip.*** *Melee Weapon Attack:* +9 to hit, reach 15 ft., one target. *Hit:* 14 (2d8 + 5) slashing damage plus 7 (2d6) poison damage, and the target must succeed on a DC 16 Constitution saving throw or become poisoned for 1 minute. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

---

### Legendary Actions

The forest guardian can take 3 legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The forest guardian regains spent legendary actions at the start of its turn.

***Wooden Club.*** The forest guardian makes a wooden club attack.

***Entwining Roots (Costs 2 Actions).*** The forest guardian magically causes grass and vines to grow rapidly from the ground in a 20-foot radius centered on itself. The area becomes difficult terrain, and any creature that starts its turn in the area must succeed on a DC 16 Strength saving throw or have its speed reduced to 0 until the start of its next turn.

***Healing Surge (Costs 3 Actions).*** The forest guardian regains 30 hit points.
"""

content_prompt = f"You are a NPC content generator of D&D. Describe NPC's appearance, personality traits, backstory, motivations, notable abilities or skills, interactions with player characters, and any relevant quest or plot hooks related to NPC's character. Include a stat block detailing NPC's combat capabilities, armor, weapons, and special abilities. You can create descriptions and stat blocks. When you create a description, you have to include the stat and ability block. Also you should include the 'Action' section. But 'Legendary Actions' section is optional. But sometimes, you should add the 'Legendary Actions'. For the ability part, you can use short words like 'Str', 'Dex' for 'Strength', 'Dexterity' and so on. If you get additional features, you can update the NPC content. If the user wants a new NPC, all items, starting with the NPC name, must be updated to a completely different words. If the inputed prompt is same as before, you have to generate completely different words from name to content. That is not updating NPC case, don't use the repeated word. You need to create NPC names that are attractive, scary, and human. Don't make general NPC name style, like 'Forest Stalker', 'Sylvan Stalker' and so on. You must format the NPC content in a homebrewery markdown. Even if the provided information is limited, you should interpret the user's intention and create the content accordingly. And if the user wants multiple NPCs, you should generate multiple NPCs. For example: If the user provides like that: 'NPC live in forest', your response should be like that: '{markdown_sample}'. Like this example, you should re-generate only related parts from the last content and continue this format for subsequent requests"

content_sample_message = [
    {
        "role": "system",
        "content": content_prompt
    },
    {
        "role": "user",
        "content": f"Hello! I need you to NPC content and return it to me as homebrewery markdown content. Here's an example: If I give you like that: 'NPC live in forest', I need you to say like that: '{markdown_sample}'"
    },
    {
        "role": "assistant",
        "content": "Sure thing!"
    }
]

start_prompt = "You are a NPC content generator. You should create a start prompt for generating NPC content of Dungeons & Dragons. Start prompt should be under 10~20 words. Don't specify the NPC's features like NPC name and so on. Give me a start prompt for generating NPC content"

# Generate NPC content from user's chat history
def generate_content(message_list, last_content):
    messages = content_sample_message + message_list

    if last_content != "":
        messages[-1]["content"] += "This is last generated NPC content : " + last_content

    response = openai.ChatCompletion.create(
        model = CHAT_COMPLETION_MODEL,
        messages = messages,
    )

    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]

        # pattern = r'<npcs>(.*?)</npcs>'
        # results = re.findall(pattern, assistant_reply, re.DOTALL)
        print(f"---- {assistant_reply}")
        npc_item = { "content": assistant_reply, "prompt": message_list }
        insert_res = npc_model.create(npc_item)
        return assistant_reply
    else:
        return "Error"

# Generate question for getting information to generate NPC content
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
    
# Save generated NPC content
def save_updated_content(message_list, updated_content):
    npc_item = { "content": updated_content, "prompt": message_list }
    inserted_id = npc_model.create(npc_item)

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
        
# Generate NPC start prompt for NPC content
def get_npc_start_prompt():
    response = openai.Completion.create(model=COMPLETION_MODEL, prompt=start_prompt, max_tokens=20)
    
    if response and response.choices:
        assistant_reply = response.choices[0].text
        return assistant_reply
    return ""

