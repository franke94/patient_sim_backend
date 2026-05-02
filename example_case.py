import json

from app.database import SessionLocal
from app.models import Case

db = SessionLocal()

case = Case(
    title = "ACS",
    case_description= "Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    address="Brückstraße 4 66131 Saarbrücken",
    gps_lat=50.93,
    gps_lng= 7.01,
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    caller_prompt= json.dumps("Du spielst eine Person, die in Deutschland die 112 wählt. Du bist aufgeregt, sprichst in kurzen Sätzen und gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben was du selbst siehst oder erlebst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen." 
    "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
    "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n DU beobachtest wie dein Mann typische Herzinfarktsympthome hat: Schmerzen in der Brust, ausstrahlend in den linken Arm, Kaltschweißig, Atmenot. Er hat eine bekannte KHK und Bluthochdruck, ist Raucher."
    "Die Adresse des Notfall ist: Hauptstraße 123, 66123 Saarbrücken, du solltest die Adresse manchmal nur zögerlich rausgeben, weil du aufgeregt bist, aber du wohnst dort und weißt natürklich die Addresse."
    "Dein Name ist: Liselotte Müller,  du bist medizinischer Laie und kannst du beschreiben was du siehst."
    "Der Name des Patienten ist: Herbert Müller, es ist dein Ehemann.")
)

db.add(case)
db.commit()
db.refresh(case)

print(f"Case ID:{case.id}")
print(f"Created at:{case.created_at}")

loaded = db.get(Case, case.id)
print(f"Loaded title: {loaded.title}")
print(f"Loaded calls (Liste): {loaded.calls}") #Zeigt noch eine leere Liste aus calls, zeigt aber das forward-verhalten

db.close()