import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chat_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

import base64

def get_image_response(prompt, response_type):
    # Generate image with OpenAI
    response = openai.images.generate(model="gpt-image-1", prompt=prompt)
    image_base64 = response.data[0].b64_json

    if response_type.lower() == "base64":
        # Return base64 string in JSON
        return {"base64": image_base64, "version": "0.1.0"}
    elif response_type.lower() == "image":
        # Return raw bytes for Flask send_file
        return base64.b64decode(image_base64)

