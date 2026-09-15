from fastapi import FastAPI
from pydantic import BaseModel

from app.core.container import create_orchestrator


app = FastAPI(
    title="FrontierAI",
    version="0.1.0",
    description="Frontier AI orchestration platform",
)

orchestrator = create_orchestrator()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


@app.get("/")
def root():
    return {
        "name": "FrontierAI",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/process")
async def process_request(request: ChatRequest):
    result = await orchestrator.process(
        request.message,
        conversation_id=request.conversation_id,
    )

    return result