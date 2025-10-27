import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chat_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_image_response(prompt, response_type):
    response = openai.images.generate(model="gpt-image-1", prompt=prompt)
    image_base64 = response.data[0].b64_json

    if response_type == "base64":
        return {"base64": image_base64, "version": "0.1.0"}
    else:
        filename = "image.png"
        with open(filename, "wb") as f:
            f.write(image_base64.encode())
        return {"image": filename, "version": "0.1.0"}
