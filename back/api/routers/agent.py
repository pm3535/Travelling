from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from back.core.security import get_current_user_id
from back.schemas import ChatRequest
from back.agent.graph import run_agent_stream


router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)


@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    Stream agent responses via Server-Sent Events.
    Frontend reads with EventSource or fetch + ReadableStream.
    """

    async def event_stream():

        async for chunk in run_agent_stream(
            messages=request.messages,
            user_id=user_id,
            trip_id=request.trip_id,
        ):
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )