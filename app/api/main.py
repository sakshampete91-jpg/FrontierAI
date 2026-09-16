from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.core.container import create_orchestrator


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"


app = FastAPI(
    title="FrontierAI API",
    version="1.0.0",
    description="Local AI assistant API.",
)


orchestrator = create_orchestrator()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    request_id: str
    response: str | None
    intent: str
    status: str
    research: dict[str, Any] | None = None
    trace: dict[str, Any] | None = None


@app.get(
    "/",
    include_in_schema=False,
)
async def frontend() -> FileResponse:
    return FileResponse(
        INDEX_FILE
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:

    # Generate a unique ID for this API request.
    request_id = str(uuid4())

    result = await orchestrator.process(
        request.message,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        request_id=request_id,

        response=result.get(
            "response"
        ),

        intent=result.get(
            "intent",
            "unknown",
        ),

        status=result.get(
            "status",
            "unknown",
        ),

        research=result.get(
            "research"
        ),

        trace=result.get(
            "trace"
        ),
    )


app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR
    ),
    name="static",
)