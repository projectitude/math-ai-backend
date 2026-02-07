from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from openai import OpenAI  # OpenAI SDK
import base64
import json

# OpenAI client (uses OPENAI_API_KEY from environment)
client = OpenAI()

app = FastAPI()

# Allow your frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def guess_mime_type(filename: str) -> str:
    """Very simple MIME type detection based on file extension."""
    lower = filename.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".gif"):
        return "image/gif"
    # Default
    return "image/jpeg"


@app.post("/api/solve-math")
async def solve_math(
    question: str = Form(""),
    images: Optional[List[UploadFile]] = File(None),
):
    """
    Main math solver endpoint.

    - Accepts a text question (optional)
    - Accepts 0 or more uploaded images (screenshots, photos, etc.)
    - Sends everything to an OpenAI vision model
    - Returns a final answer + step-by-step explanation
    """

    # ============= 1) Encode images as base64 data URLs =============
    image_parts = []
    image_names = []

    if images:
        for img in images:
            # Read image bytes
            content = await img.read()
            if not content:
                continue

            image_names.append(img.filename)

            # Base64 encode
            b64 = base64.b64encode(content).decode("utf-8")
            mime = guess_mime_type(img.filename)

            image_parts.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{mime};base64,{b64}",
                }
            )

    # ============= 2) Build instructions for the model =============
    base_instructions = """
You are a careful, step-by-step math tutor.

You receive:
- A text question (may be empty).
- 0 or more images that may contain a math problem (screenshots, photos, handwritten notes, etc.).

Your job:
1. Carefully read any math problem shown in the image(s).
2. Combine that with the text question (if any).
3. Solve the problem correctly.
4. Return ONLY valid JSON in this exact format (no backticks, no extra text):

{
  "final_answer": "...",
  "steps": "..."
}

- "final_answer" = short final numeric/symbolic answer.
- "steps" = clear explanation with multiple steps, formatted as readable text.
- If the image is unclear, say that in the steps and explain what is missing.
"""

    # Put everything into one "input_text"
    combined_text = base_instructions + "\n\nStudent text question (may be empty):\n"
    combined_text += (question or "[no typed question, only image(s)].")

    # ============= 3) Create input for Responses API =============
    # This list will always have the instructions/text,
    # and will include image parts if any were uploaded.
    content_items = [{"type": "input_text", "text": combined_text}]
    content_items.extend(image_parts)

    # Use a vision-capable model (gpt-4.1-mini is cheap + supports images)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": content_items,
            }
        ],
    )

    raw_text = response.output_text  # The model's text output as a single string

    # ============= 4) Parse JSON safely =============
    final_answer = "Could not parse answer"
    steps = raw_text

    try:
        data = json.loads(raw_text)
        final_answer = data.get("final_answer", final_answer)
        steps = data.get("steps", steps)
    except Exception:
        # If the model did not return valid JSON, just show raw text in steps
        pass

    # Optionally add info about images used
    if image_names:
        steps += "\n\n(Images analyzed: " + ", ".join(image_names) + ")"

    return {
        "answer": final_answer,
        "steps": steps,
    }
