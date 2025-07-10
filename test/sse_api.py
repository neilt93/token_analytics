import json
import os
import time

import httpx
import sseclient
from ulid import ULID

# Environment parameters.
_AUTH_TOKEN = os.getenv("JWT_TOKEN")
_CHATS_URL = os.getenv("CHATS_URL")
_AGENTS_URL = os.getenv("AGENTS_URL")
_CUSTOM_AUTH = os.getenv("CUSTOM_AUTH")
_TEST_EMAIL = os.getenv("TEST_EMAIL")

# Optionally import Langfuse Generation for type hinting
try:
    from langfuse.model import Generation
except ImportError:
    Generation = None

# Get new chat identifier before asking questions.
def get_chat_id() -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_AUTH_TOKEN}",
        "x-custom-auth": _CUSTOM_AUTH
    }
    data = {
        "chat_name": "",
        "start_time": "2025-01-19T18:34:00.000Z"
    }
    response = httpx.post(_CHATS_URL, headers=headers, json=data)
    return response.json()


def get_response(chat_id: str, agent_id: str, user_query: str, generation=None):
    url = f"{_AGENTS_URL}/{agent_id}"
    http_client = httpx.Client(timeout=60)
    # Ensure request_id is greater than chat_id
    time.sleep(0.01)
    request_id = str(ULID())
    while request_id <= chat_id:
        time.sleep(0.01)
        request_id = str(ULID())
    headers = {
        "Authorization": f"Bearer {_AUTH_TOKEN}",
        "Accept": "text/event-stream",
        "x-custom-auth": _CUSTOM_AUTH,
        "x-user-id": _TEST_EMAIL
    }
    payload = {
        "id": request_id,
        "chat_id": chat_id,
        "content": {
            "capability": "assist",
            "request_payload": {
                "parts": [
                    {
                        "prompt": user_query,
                        "files_ids": []
                    }
                ]
            }
        }
    }
    with http_client.stream("POST", url, headers=headers, json=payload) as response:
        answer = ""
        first_token_time = None
        start_time = time.time()
        if response.status_code == 200:
            sse_client = sseclient.SSEClient(response.iter_bytes())
            for event in sse_client.events():
                if first_token_time is None:
                    first_token_time = time.time()
                try:
                    data = json.loads(event.data)
                    event_name = data.get("event_name", "unknown")
                    if event_name == "final_response" and "content" in data:
                        print(data["content"], end="", flush=True)
                        answer += data["content"]
                except Exception:
                    pass
            print()
        else:
            raw_content = response.read()
            try:
                print(f"[ERROR] Agent response: {raw_content.decode('utf-8')}")
            except Exception:
                print(f"[ERROR] Agent response (raw bytes): {raw_content}")
        http_client.close()
        response.close()
        time_to_first_token = None
        if first_token_time is not None:
            time_to_first_token = (first_token_time - start_time) * 1000
        if generation is not None:
            generation.end(
                output=answer,
                usage={"ttfb": time_to_first_token}
            )
        return answer, time_to_first_token



