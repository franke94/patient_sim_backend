from sqlalchemy.orm import Session

from app.models import Call, ChatMessage, Case
from app.models.enums import MessageRoleEnum
from app.simulation.llm import LLMMessage, get_llm_client


#Wird mal testweise ersetzt durch einen vom System vorgegeben Caller Prompt, um mehr Variation reinzukriegen.
def _build_system_prompt(case: Case) -> str:
    return ( "Du spielst eine Person, die in Deutschland die 112 wählt. "
        "Du bist aufgeregt, sprichst in kurzen Sätzen und gibst Informationen primär dann, wenn der Calltaker danach fragt."
        "Du bist medizinischer Laie und kannst nur beschreiben was du selbst siehst oder erlebst."
        "Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen. "
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        f"Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n{case.case_description}"
        f"Die Adresse des Notfall ist: {case.address}, du solltest die Adresse manchmal nur zögerlich rausgeben, wenn du dir nocht ganz sicher bist. "
        f"Dein Name ist:{case.caller_name}, du bist medizinischer Laie und kannst du beschreiben was du siehst."
        f"Der Name des Patienten ist: {case.patient_name}"
    )


def _to_llm_messages(messages: list[ChatMessage]) -> list[LLMMessage]:
    ordered = sorted(messages, key = lambda m: m.order_index)
    return [LLMMessage(role=m.role.value, content=m.content) for m in ordered]

def run_caller_turn(call: Call, db: Session) -> ChatMessage:
    """Generiert die nächste Anrufer-Nachricht für den gegebenen Call """
    #system_prompt = _build_system_prompt(call.case)

    history = _to_llm_messages(call.messages)

    client = get_llm_client()
    result = client.chat(call.case.caller_prompt, history)
    reply_text = result.text

    last_order = max((m.order_index for m in call.messages), default=-1)
    reply = ChatMessage(
        call=call,
        role=MessageRoleEnum.ASSISTANT, #Auf Caller umbauen?
        content=reply_text,
        order_index=last_order + 1,
    )
    db.add(reply)  # Die Funktion commited absichtilich nicht, damit bei einem LLM crash nicht die user Message alleine in der db landet
    return reply