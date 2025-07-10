import os
import time
import random
import threading

from dotenv import load_dotenv
from langfuse import Langfuse
import sse_api
from config import read_config

# Load env vars
load_dotenv()

# Load agent config
_AGENTS, _TAGS = read_config(os.getenv("CONFIG_YAML_PATH"))
_NUM_AGENTS = len(_AGENTS)
_RANDOM = False

# Langfuse setup
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="https://us.cloud.langfuse.com"
)

# Global response holders
responses = [None] * _NUM_AGENTS
threads = [None] * _NUM_AGENTS


def get_agent_response(i, agent_id, chat_id, prompt, prompt_span=None, prompt_id="", prompt_subid="", agent_name=""):
    time.sleep(0.5)
    generation = None

    if prompt_span:
        generation = prompt_span.start_generation(
            name=f"agent-{agent_id}-prompt",
            input=prompt,
            metadata={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "chat_id": chat_id,
                "prompt_id": prompt_id,
                "prompt_subid": prompt_subid
            }
        )

    try:
        response, ttfb = sse_api.get_response(chat_id, agent_id, prompt)
        if generation:
            generation.update(output=response)
            generation.update(usage={"ttfb": ttfb})
            generation.end()
        responses[i] = (response, ttfb)
    except Exception as e:
        print(f"[ERROR] Agent {agent_id} failed: {e}")
        if generation:
            generation.update(output=f"[ERROR] {e}")
            generation.end()
        responses[i] = ("[ERROR]", 0)


def get_agent_responses(chat_ids, prompt, prompt_id="", prompt_subid="", prompt_span=None):
    """
    Dispatches the prompt to all agents in parallel and collects their responses.
    """
    global responses, threads
    responses = [None] * _NUM_AGENTS
    threads = [None] * _NUM_AGENTS

    if _RANDOM:
        random.shuffle(chat_ids)

    for i, agent_name in enumerate(_AGENTS.keys()):
        threads[i] = threading.Thread(
            target=get_agent_response,
            args=(i, _AGENTS[agent_name], chat_ids[i], prompt, prompt_span, prompt_id, prompt_subid, agent_name)
        )
        threads[i].start()

    for i in range(_NUM_AGENTS):
        threads[i].join()

    return responses


# Export these for use in run_sentient.py
__all__ = ["get_agent_responses", "_AGENTS", "_NUM_AGENTS"]
