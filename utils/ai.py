import re
import asyncio
from groq import Groq
from utils.config import config
from utils.memory import get_user_memory, save_memory
from utils.logger import ai_logger

groq_client = Groq(api_key=config["GROQ_API_KEY"])

_SYSTEM_PROMPT = """
You are Aarshi Lodia.

Personality:
arrogant, impatient, narcissistic, dramatic.

You act like you're royalty and a victim and your problems are more important than everyone else.

Rules:
- Respond in two to three natural sentences
- Maximum ~40 words
- Minimum ~15 words
- Never exceed two sentences
- No roleplay
- No *asterisks*
- No stage directions
- Speak naturally like voice conversation
"""

_PERSONA_PROMPT = """
Analyze the user's behavior and summarize personality traits.
Return short bullet points only.
"""


async def update_persona(user_id: int):
    user_mem = get_user_memory(user_id)
    history = "\n".join(user_mem["history"][-10:])

    if not history:
        return

    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            messages=[
                {"role": "system", "content": _PERSONA_PROMPT},
                {"role": "user", "content": history}
            ]
        )

    try:
        completion = await asyncio.to_thread(_call)
        notes = completion.choices[0].message.content.split("\n")
        user_mem["persona_notes"] = notes[:5]
        save_memory()
        ai_logger.info(f"Updated persona for user {user_id}")
    except Exception as e:
        ai_logger.error(f"Persona update failed for user {user_id}: {e}")


async def ask_ai(user_id: int, username: str, prompt: str) -> str:
    user_mem = get_user_memory(user_id)
    history = "\n".join(user_mem["history"][-6:])
    notes = "\n".join(user_mem["persona_notes"])

    context = f"""
User: {username}

Known traits:
{notes}

Recent conversation:
{history}

New message from {username}:
{prompt}
"""

    def _call():
        return groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            temperature=0.7,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ]
        )

    try:
        completion = await asyncio.to_thread(_call)
        response = completion.choices[0].message.content
    except Exception as e:
        ai_logger.error(f"Groq API error for user {user_id}: {e}")
        raise

    response = re.sub(r"\*.*?\*", "", response)
    response = re.sub(r"_.*?_", "", response)
    response = response.strip()

    user_mem["history"].append(f"User: {prompt}")
    user_mem["history"].append(f"Aarshi: {response}")
    user_mem["history"] = user_mem["history"][-12:]
    save_memory()

    user_messages = [h for h in user_mem["history"] if h.startswith("User:")]
    if len(user_messages) % 6 == 0:
        asyncio.create_task(update_persona(user_id))

    ai_logger.info(f"Response generated for user {user_id} ({username})")
    return response
