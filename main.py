from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

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
    Test endpoint:
    - Receives text question
    - Receives uploaded images (if any)
    - Returns a dummy answer + image names
    Next step: connect real AI logic here.
    """

    image_names = []
    if images:
        for img in images:
            image_names.append(img.filename)

    answer = "Backend is working ✅"
    steps = (
        "Received question:\n"
        + (question or "[no text question]")
        + "\n\nImages uploaded:\n"
        + (", ".join(image_names) if image_names else "No images uploaded.")
        + "\n\n(Next step: connect real AI here.)"
    )

    return {
        "answer": answer,
        "steps": steps
    }
