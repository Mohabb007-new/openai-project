import openai
import os
import base64
from typing import Optional

# configure openai key from env if present
openai.api_key = os.getenv("OPENAI_API_KEY")

# Small 1x1 PNG (transparent) base64 used for test fallbacks
_TEST_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


def _is_fake_mode() -> bool:
    """Decide whether to run in fake/test mode.

    Priority: FORCE_FAKE_OPENAI env var -> Flask current_app.TESTING -> absence of OPENAI_API_KEY
    """
    # explicit override to force fake
    if os.getenv("FORCE_FAKE_OPENAI"):
        return True

    # if a real API key is present, prefer real mode even during TESTING
    if os.getenv("OPENAI_API_KEY"):
        return False

    try:
        # check flask testing flag when available
        from flask import current_app

        if current_app and current_app.config.get("TESTING"):
            return True
    except Exception:
        pass

    # fallback: if no API key configured, default to fake
    return True


def get_chat_response(prompt: str) -> str:
    """Return a chat response. In fake mode return deterministic text."""
    if _is_fake_mode():
        return f"(test) Echo: {prompt}"

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def get_image_response(prompt: str, response_type: str) -> Optional[bytes | dict]:
    """Return either a JSON with base64 or raw image bytes.

    If running in fake mode, return a small test PNG (base64 or bytes).
    """
    if _is_fake_mode():
        image_base64 = _TEST_PNG_B64
    else:
        response = openai.images.generate(model="gpt-image-1", prompt=prompt)
        image_base64 = response.data[0].b64_json

    if response_type.lower() == "base64":
        return {"base64": image_base64, "version": "0.1.0"}
    elif response_type.lower() == "image":
        return base64.b64decode(image_base64)
    else:
        return None

