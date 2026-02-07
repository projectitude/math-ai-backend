from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from openai import OpenAI  # NEW: OpenAI SDK
import json

# Create OpenAI client (reads OPENAI_API_KEY from env)
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


@app.post("/api/solve-math")
async def solve_math(
    question: str = Form(""),
    images: Optional[List[UploadFile]] = File(None),
):
    """
    Main math solver endpoint.

    - Receives text question
    - Receives uploaded images (currently not sent to AI yet)
    - Sends the question to OpenAI
    - Returns final answer + step-by-step explanation
    """

    # Collect image filenames for now (we'll wire true vision later)
    image_names = []
    if images:
        for img in images:
            image_names.append(img.filename)

    # Build a math-tutor style prompt
    base_instructions = """
You are a careful, step-by-step math tutor.

Solve the student's math problem and then return ONLY valid JSON
using this exact format (no extra text, no backticks):

{
  "final_answer": "...",
  "steps": "..."
}

- "final_answer" = short final numeric/symbolic answer.
- "steps" = clear, student-friendly explanation in multiple steps.

If the question is ambiguous, state your assumptions in the steps.
"""

    full_prompt = base_instructions + f"\n\nStudent question:\n{question}\n"

    # Call OpenAI Responses API
    response = client.responses.create(
        model="gpt-5.2",  # you can switch to another model if you like
        input=full_prompt,
    )

    # Extract the text output
    raw_text = response.output_text  # SDK helper to join all text parts :contentReference[oaicite:1]{index=1}

    # Try to parse the JSON the model returns
    final_answer = "Could not parse answer"
    steps = raw_text

    try:
        data = json.loads(raw_text)
        final_answer = data.get("final_answer", final_answer)
        steps = data.get("steps", steps)
    except Exception:
        # If it didn't return valid JSON, just show the raw text in steps
        pass

    # Optionally mention images in the explanation
    if image_names:
        steps += "\n\n(Images provided: " + ", ".join(image_names) + ")"

    return {
        "answer": final_answer,
        "steps": steps,
    }
