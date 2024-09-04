import os

import torch
from dotenv import load_dotenv
from fastapi import FastAPI
from huggingface_hub._login import login
from pydantic import BaseModel

from dating_llm.base import BaseTextGenerationLLM


class Query(BaseModel):
    prompt: str


load_dotenv()

app = FastAPI()

login(token=os.getenv("HUGGINGFACE_TOKEN"))


model = BaseTextGenerationLLM(
    os.getenv("DEFAULT_LLM_MODEL"),
    torch_dtype=torch.bfloat16,
)


# curl  -X POST http://localhost:4321/query -d '{"prompt":"how are you?"}' -H "Content-Type: application/json"
@app.post("/query")
async def predict(query: Query):
    response = model.generate(query.prompt)
    query_length = len(query.prompt)
    return {"response": response[query_length + 1:]}
