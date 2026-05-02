from app.simulation.llm import get_llm_client, LLMMessage
client = get_llm_client()
reply = client.chat(
    "Du bist ein freundlicher Assistent.",
    [LLMMessage(role="user", content="Sag in einem Satz hallo.")],
)
print(reply)