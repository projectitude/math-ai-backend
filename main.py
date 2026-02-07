{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from fastapi import FastAPI, File, UploadFile, Form\
from fastapi.middleware.cors import CORSMiddleware\
from typing import List, Optional\
\
app = FastAPI()\
\
app.add_middleware(\
    CORSMiddleware,\
    allow_origins=["*"],\
    allow_credentials=True,\
    allow_methods=["*"],\
    allow_headers=["*"],\
)\
\
@app.post("/api/solve-math")\
async def solve_math(\
    question: str = Form(""),\
    images: Optional[List[UploadFile]] = File(None),\
):\
    extracted = []\
    if images:\
        for img in images:\
            extracted.append(f"Image received: \{img.filename\}")\
\
    answer = "This is a demo backend response."\
    steps = (\
        "Your question was:\\n"\
        + question\
        + "\\n\\n"\
        + "\\n".join(extracted)\
        + "\\n\\n(Next step: connect real AI here)"\
    )\
\
    return \{\
        "answer": answer,\
        "steps": steps\
    \}\
}