
import asyncio
from dataclasses import dataclass
from typing import Optional
import openai

@dataclass
class MessageResponse:
    response_text: str
    confidence: float
    suggested_action: str
    channel_formatted_response: str
    error: Optional[str]

SYSTEM_PROMPT = """
You are a telecom support agent helping customers.
Be polite and helpful.

Rules:
- If channel is voice: response must be under 2 sentences.
- If channel is chat or whatsapp: response can be longer.
- Suggest actions like troubleshooting, billing help, or escalation.
"""


async def handle_message(customer_message: str, customer_id: str, channel: str) -> MessageResponse:

    if not customer_message.strip():
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="none",
            channel_formatted_response="",
            error="Empty message provided"
        )

    try:
        response = await asyncio.wait_for(
            openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": customer_message}
                ]
            ),
            timeout=10
        )

        ai_text = response["choices"][0]["message"]["content"]

        return MessageResponse(
            response_text=ai_text,
            confidence=0.85,
            suggested_action="assist_customer",
            channel_formatted_response=f"[{channel}] {ai_text}",
            error=None
        )

    except asyncio.TimeoutError:
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="retry",
            channel_formatted_response="",
            error="API timeout"
        )

    except openai.error.RateLimitError:

      
        await asyncio.sleep(2)

        return MessageResponse(
            response_text="Temporary service delay. Please try again.",
            confidence=0.0,
            suggested_action="retry",
            channel_formatted_response="Service delay",
            error="Rate limit reached"
        )
