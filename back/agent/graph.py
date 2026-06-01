import json
from re import I
from typing import AsyncGenerator, List, Annotated
from openai import AsyncOpenAI
from back.core.config import settings
from back.schemas import ChatMessage
from back.agent.tools import TOOLS, execute_tool

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert AI travel assistant for TravelApp.
You help users plan trips, find flights and hotels, get weather info, and discover destinations.
 
You have access to tools:
- search_flights: search for available flights between two cities
- search_hotels: find hotels in a city
- get_weather: get current weather for any city
- search_destinations: search the destination database
 
Always be helpful, concise, and suggest concrete options.
When planning a trip, proactively offer to search for flights and hotels.
"""

async def run_agent_stream(messages: List[ChatMessage], user_id: str, trip_id: str | None = None) -> AsyncGenerator[str, None]:
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history +=  [{"role": m.role, "content": m.content} for m in messages]

    while True:
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages= history,
            tools=TOOLS,
             tool_choice="auto",
            stream=True,
            max_tokens=1000,
        )

        full_content = ""
        tool_calls_raw = {}


        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            if delta.content:
                full_content += delta.content
                yield json.dump ({"type": "text", "content": delta.content})

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_raw:
                        tool_calls_raw[idx] = {
                            'id': tc.id or "",
                            'name':tc.function.name if tc.function else '',
                            'args': '',
                        }

                    if tc.id:
                        tool_calls_raw[idx]['id'] = tc.id
                    if tc.function:
                        tool_calls_raw[idx]['name'] = tc.function.name
                    if tc.function.arguments:
                        tool_calls_raw[idx]['args'] += tc.function.arguments

        if not tool_calls_raw:
            break

        tool_calls_list = []
        for idx in sorted(tool_calls_raw.keys()):
            tc = tool_calls_raw[idx]
            tool_calls_list.append({
                "id": tc["id"],
                "type": "function",
                "function": {"name": tc["name"], "arguments": tc["args"]},
            })

            history.append({
            "role": "assistant",
            "content": full_content or None,
            "tool_calls": tool_calls_list,
            })

            for tc in tool_calls_list:
             name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except Exception:
                args = {}
 
            yield json.dumps({"type": "tool_call", "tool": name, "args": args})

            result = await execute_tool(name, args)
            yield json.dumps({"type": "tool_result", "tool": name, "result": result})
 
            history.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(result),
            })
 


