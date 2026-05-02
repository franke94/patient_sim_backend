from app.models import ABCDEAssessment, AgentRun
from app.models.enums import AgentTypeEnum, CategoryEnum, SeverityEnum, SourceEnum
from app.simulation.agents.base import BaseAgent, OutputT
from pydantic import BaseModel, Field
from app.simulation.agents.abcde_agents import ABCDEAgentOutput

"""
Der Plan: Einen Agenten der immer nach jeder neuen (Caller-)Nachricht das gesamte Gespräch analisiert und ABCDE Bewertung updatet

Dazu: 
- Prompt anpassen
- Rückgabe als A,B,C,D,E
- Rückgabe aufschlüsseln, findings in Datenbank eintragen

Offene Punkte: Wie geht es dass der Agent nach jeder Nachricht löuft?
Macht es Sinn, dass der Agent die Alten findings bekommt? 
Oder doch mehrere Agenten, als einer der nur Analysiert und weitergibt wenn es was neues gibt? Erstmal einfach anfangen, mit einem Agenten der immer Läuft 
"""

class SingleAgentOutput(BaseModel):
    """
    Verschachtelter Output
    """
    a: ABCDEAgentOutput
    b: ABCDEAgentOutput
    c: ABCDEAgentOutput
    d: ABCDEAgentOutput
    e: ABCDEAgentOutput



class SingleAgent(BaseAgent[SingleAgentOutput]):
    agent_type = AgentTypeEnum.SINGLE_AGENT
    output_schema = SingleAgentOutput

    def build_prompt(self) -> str:
        return (
        "Du bist ein medizinischer Auswertungsagent in einer Rettungsleitstelle"
        "Du erhälst ein transkribiertes Notrufgespräch und hast die Aufgabe, die medizinischen Beschreibungen zu Filtern und zu bewerten"
        "Beachte, dass du bereits läufst während das Notrufgespräch noch geführt wird. Das kann dazu führen, dass noch gar keine Informationen vorliegen. Dann sollst du nicht haluzinieren \n"
        "Geh dabei streng nach dem ABCDE-Schema vor.\n"
        "A: Atemwegsprobleme. Hier geht es wirklich nur um Probleme des Atemwegs, nicht der Atmung, die wird in B abgefragt. Also zum Beispiel verlegte Atemwege durch Allergien.\n"
        "B: Breathing. Hier geht es um Probleme mit der Atmung: Atemstörungen, keine Atmung, flache Atmung, Schmerzen bei der Atmung etc.\n"
        "C: Circulation. Hier geht es um alles was mit dem kreislauf und dem Herzen zu tun hat: Kreislaufstörungen, massiver Blutverlust, Retrosternale Schmerzen, Bluthochdruck, etc.\n"
        "D: Disability. Hier geht es um alles Neurologische und Bewusstsein. Schlaganfallsymthome, Bewusstlosigkeit, Bewusstseinseinschränkungen, Schwindet etc.\n"
        "E: Exposure. Hier geht es um den ganzen Rest, wie Schmerzen im Magen, Verletzungen die nicht für C relevant sind etc.\n"
        "Gehe streng in den drei Schritten vor:"
        "**Findings**: Suche nach Hinweisen im Gespräch und erfinde nichts dazu. Es geht hier um echte Zitate aus dem Text, die belegbar sein müssen. Wenn im Text nixhts passendes zu finden ist, dann geb eine leere Liste zurück!\n"
        "**Severity**: Beurteile die Findings streng nach den folgenden Kategorien: \n"
        "none: Es wurden keine Hinweise gefunden\n"
        "mild: Die Einschränkungen sind nur leicht, keine Lebensgefährlichen Beeinschränkungen\n"
        "severe: Die Einschränkungen können auch gravierender sein, eine lebensgefahr ist nicht auszuschließen, rasches Handeln duch den Rettungsdienst ist notwendig\n"
        "critical: Die Einschränkungen sind sehr wahrscheinlich lebensgefährlich. Der Rettungsdienst und Notarzt müssen umgehend ausrücken\n"
        "**ratinale**: Hier beschreibst du kurz und knapp, wie du von den Findings auf die Severity gekommen bist.\n"
        "Antworte nur mit folgendem JSON-Schema und keine weiteren Beschreibungen:\n"
        "{\n"
        ' "a": {findings": [string,...], "severity": "none" |"mild" | "severe" | "critical", "rationale": string}, \n'
        ' "b": {findings": [string,...], "severity": "none" |"mild" | "severe" | "critical", "rationale": string}, \n'
        ' "c": {findings": [string,...], "severity": "none" |"mild" | "severe" | "critical", "rationale": string}, \n'
        ' "d": {findings": [string,...], "severity": "none" |"mild" | "severe" | "critical", "rationale": string}, \n'
        ' "e": {findings": [string,...], "severity": "none" |"mild" | "severe" | "critical", "rationale": string} \n'
        "}"
    )

    def persist(self, output: SingleAgentOutput, run: AgentRun) -> None:
        category_mapping = [
            (CategoryEnum.A, output.a),
            (CategoryEnum.B, output.b),
            (CategoryEnum.C, output.c),
            (CategoryEnum.D, output.d),
            (CategoryEnum.E, output.e),
        ]
        for category, item in category_mapping:
            self.db.add(ABCDEAssessment(
                call_id = self.call.id,
                source=SourceEnum.AI_AGENT,
                category=category,
                findings=item.findings,
                severity=item.severity,
                agent_run_id=run.id
            ))








