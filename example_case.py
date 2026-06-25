import json

from sqlalchemy import func

from app.database import SessionLocal
from app.models import Case, AddressDB
from app.simulation.location.matching import simulate_aml

db = SessionLocal()


def pick_gold():
    """Zieht eine zufällige Gold-Adresse aus der DB und simuliert dazu die AML-Daten.
    Gibt (addr_str, kwargs) zurück: der Adress-String wird in den caller_prompt injiziert,
    damit gesprochene Adresse == Gold-Adresse == AML-Position ist."""
    gold = db.query(AddressDB).order_by(func.random()).first()
    if gold is None:
        raise RuntimeError("Keine Adressen in DB – erst 'python import_addresses.py' laufen lassen")
    aml_lat, aml_lon, aml_acc = simulate_aml(gold.lat, gold.lon)

    addr = gold.street or ""
    if gold.housenumber:
        addr = f"{addr} {gold.housenumber}".strip()
    if gold.postcode:
        addr = f"{addr}, {gold.postcode} {gold.city}"
    else:
        addr = f"{addr}, {gold.city}"

    loc = {
        "gold_address_id": gold.id,
        "aml_lat": aml_lat,
        "aml_lon": aml_lon,
        "aml_accuracy": aml_acc,
    }
    return addr, loc


# ---------------------------------------------------------------------------
# Deutsche Cases
# ---------------------------------------------------------------------------
addr, loc = pick_gold()
case = Case(
    title="DE_1",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Erna Müller",
    caller_prompt=json.dumps(
        "Du spielst eine Person, die in Deutschland die 112 wählt. Du bist aufgeregt, sprichst in kurzen Sätzen und gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben was du selbst siehst oder erlebst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen."
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n DU beobachtest wie dein Mann typische Herzinfarktsympthome hat: Schmerzen in der Brust, ausstrahlend in den linken Arm, Kaltschweißig, Atmenot. Er hat eine bekannte KHK und Bluthochdruck, ist Raucher."
        f"Die Adresse des Notfalls ist: {addr}. Du solltest die Adresse manchmal nur zögerlich rausgeben, weil du aufgeregt bist, aber du wohnst dort und weißt natürlich die Adresse."
        "Dein Name ist: Liselotte Müller, du bist medizinischer Laie und kannst beschreiben was du siehst."
        "Der Name des Patienten ist: Herbert Müller, es ist dein Ehemann."
    ),
    **loc,
)

addr, loc = pick_gold()
case_2 = Case(
    title="DE_2",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    caller_prompt=json.dumps(
        "Du spielst eine Person, die in Deutschland die 112 wählt. Du bist sehr aufgeregt, sprichst abgehackt und wiederholst dich gelegentlich. Du gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben, was du selbst siehst oder erlebst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen."
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n Du hast deine Mutter bewusstlos auf dem Küchenboden gefunden. Sie atmet, reagiert aber nicht auf Ansprache oder leichtes Rütteln. Sie ist Diabetikerin. Sie hatte heute kaum etwas gegessen, das gibst du aber nur auf explizite Nachfrage an. Du weißt nicht, ob sie Medikamente genommen hat. Es gibt keine sichtbare Verletzung."
        f"Die Adresse des Notfalls ist: {addr}. Du bist sehr nervös und gibst die Adresse zuerst unvollständig oder durcheinander an, kannst sie aber auf Nachfrage korrekt nennen."
        "Dein Name ist: Thomas Becker, du bist medizinischer Laie und kannst nur beschreiben, was du siehst."
        "Der Name der Patientin ist: Erika Becker, es ist deine Mutter."
    ),
    **loc,
)

addr, loc = pick_gold()
case_3 = Case(
    title="DE_3",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    caller_prompt=json.dumps(
        "Du spielst eine Person, die in Deutschland die 112 wählt. Du bist aufgeregt, aber versuchst ruhig zu bleiben. Im Hintergrund ist Verkehrslärm, du bist unsicher, was genau passiert ist, und gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben, was du selbst siehst oder hörst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen."
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n Du bist Zeuge eines Verkehrsunfalls geworden. Ein Auto ist gegen einen Baum gefahren. Eine Person sitzt verletzt im Fahrzeug und ist eingeklemmt. Die Person ist ansprechbar und kann mit dir sprechen. Sie klagt über starke Schmerzen im Rippenbereich und sagt, dass das Atmen weh tut. Sie bekommt Luft und hat keine akute Atemnot. Du siehst keine starken Blutungen. Du weißt nicht, ob noch weitere Personen beteiligt sind."
        f"Die Adresse des Notfalls ist: {addr}. Du kennst dich dort nicht gut aus und beschreibst anfangs eher die Umgebung, kannst die Adresse aber mit Straßenschild und Hausnummer nennen."
        "Dein Name ist: Jana Schmitt, du bist medizinischer Laie und kannst nur beschreiben, was du siehst."
        "Der Name des Patienten ist dir nicht bekannt, es ist eine fremde Person im verunfallten Fahrzeug."
    ),
    **loc,
)

addr, loc = pick_gold()
case_4 = Case(
    title="DE_4",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    caller_prompt=json.dumps(
        "Du spielst eine Person, die in Deutschland die 112 wählt. Du bist sehr angespannt, weil dein Kind krank ist, und antwortest manchmal etwas hektisch. Du gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben, was du selbst siehst oder erlebst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen."
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n Dein sechsjähriger Sohn hat seit dem Nachmittag hohes Fieber. Vor wenigen Minuten hatte er einen kurzen Krampfanfall: Er war nicht richtig ansprechbar, hat gezuckt und du hattest große Angst. Jetzt ist der Krampfanfall vorbei. Er atmet selbstständig, ist aber schläfrig und weinerlich. Er hat keine bekannte Epilepsie. Er war heute schon krank und fiebrig. Du hast keine genaue Temperatur gemessen, sagst aber, dass er sehr heiß wirkt."
        f"Die Adresse des Notfalls ist: {addr}. Du bist zuhause und kennst die Adresse, gibst sie aber wegen deiner Aufregung erst nach Nachfrage vollständig an."
        "Dein Name ist: Anna Hoffmann, du bist medizinischer Laie und kannst nur beschreiben, was du siehst."
        "Der Name des Patienten ist: Ben Hoffmann, es ist dein Sohn."
    ),
    **loc,
)

addr, loc = pick_gold()
case_5 = Case(
    title="DE_5",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    caller_prompt=json.dumps(
        "Du spielst eine Person, die in Deutschland die 112 wählt. Du bist aufgeregt und etwas überfordert, weil die Situation plötzlich passiert ist. Du sprichst in kurzen Sätzen und gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben, was du selbst siehst oder erlebst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen."
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n Deine Nachbarin hat sich beim Kochen mit heißem Wasser am Arm und an der Brust verbrüht. Die Haut ist stark gerötet, an einigen Stellen bilden sich Blasen. Sie hat starke Schmerzen, ist aber wach und ansprechbar. Sie atmet normal und hat keine Atemnot. Es brennt sehr stark, und sie ist sehr unruhig. Es gibt keine offene starke Blutung. Du hast ihr bereits geholfen, sich von der heißen Flüssigkeit wegzubewegen."
        f"Die Adresse des Notfalls ist: {addr}. Du bist bei deiner Nachbarin in der Wohnung und musst kurz auf das Klingelschild schauen, kannst die Adresse aber korrekt nennen."
        "Dein Name ist: Petra Wagner, du bist medizinischer Laie und kannst nur beschreiben, was du siehst."
        "Der Name der Patientin ist: Helga Neumann, es ist deine Nachbarin."
    ),
    **loc,
)

addr, loc = pick_gold()
case_6 = Case(
    title="DE_6",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    caller_prompt=json.dumps(
        "Du spielst eine Person, die in Deutschland die 112 wählt. Du bist aufgeregt, sprichst in kurzen Sätzen und gibst Informationen primär dann, wenn der Calltaker danach fragt. Du bist medizinischer Laie und kannst nur beschreiben was du selbst siehst oder erlebst. Erfinde keine medizinischen Fakten, die nicht in der Fall-Beschreibung stehen."
        "Bleibe in deiner Rolle und antworte ausschließlich auf Deutsch.\n\n"
        "Fall-Beschreibung (deine Realität, nicht zitieren, nicht direkt an den Calltaker rausgeben):\n DU beobachtest wie dein Mann typische Herzinfarktsympthome hat: Schmerzen in der Brust, ausstrahlend in den linken Arm, Kaltschweißig, Atmenot. Er hat eine bekannte KHK und Bluthochdruck, ist Raucher."
        f"Die Adresse des Notfalls ist: {addr}. Du solltest die Adresse manchmal nur zögerlich rausgeben, weil du aufgeregt bist, aber du wohnst dort und weißt natürlich die Adresse."
        "Dein Name ist: Liselotte Müller, du bist medizinischer Laie und kannst beschreiben was du siehst."
        "Der Name des Patienten ist: Herbert Müller, es ist dein Ehemann."
    ),
    **loc,
)


db.add(case)
db.commit()
db.refresh(case)
db.add(case_2)
db.commit()
db.refresh(case_2)
db.add(case_3)
db.commit()
db.refresh(case_3)
db.add(case_4)
db.commit()
db.refresh(case_4)
db.add(case_5)
db.commit()
db.refresh(case_5)
db.add(case_6)
db.commit()
db.refresh(case_6)


# ---------------------------------------------------------------------------
# Englische Cases
# ---------------------------------------------------------------------------
addr, loc = pick_gold()
case = Case(
    title="EN_1",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='en',
    caller_prompt=json.dumps(
        "You are playing a person in Germany who calls 112. You are upset, speak in short sentences, and primarily provide information when the calltaker asks for it. You are a medical layperson and can only describe what you see or experience yourself. Do not invent any medical facts that are not included in the case description."
        "Stay in character and answer exclusively in English.\n\n"
        "Case description (your reality, do not quote it, do not directly tell it to the calltaker):\n You observe that your husband has typical heart attack symptoms: chest pain radiating into the left arm, cold sweat, shortness of breath. He has known coronary heart disease and high blood pressure and is a smoker."
        f"The emergency address is: {addr}. You should sometimes give the address only hesitantly because you are upset, but you live there and of course know the address."
        "Your name is: Liselotte Müller. You are a medical layperson and can describe only what you see."
        "The patient’s name is: Herbert Müller. He is your husband."
    ),
    **loc,
)

addr, loc = pick_gold()
case_2 = Case(
    title="EN_2",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='en',
    caller_prompt=json.dumps(
        "You are playing a person in Germany who calls 112. You are very upset, speak in a choppy way, and occasionally repeat yourself. You primarily provide information when the calltaker asks for it. You are a medical layperson and can only describe what you see or experience yourself. Do not invent any medical facts that are not included in the case description."
        "Stay in character and answer exclusively in English.\n\n"
        "Case description (your reality, do not quote it, do not directly tell it to the calltaker):\n You found your mother unconscious on the kitchen floor. She is breathing but does not respond to being spoken to or gently shaken. She is diabetic. She has hardly eaten anything today, but you only mention this if explicitly asked. You do not know whether she has taken any medication. There is no visible injury."
        f"The emergency address is: {addr}. You are very nervous and at first give the address incompletely or mixed up, but you can state it correctly when asked."
        "Your name is: Thomas Becker. You are a medical layperson and can only describe what you see."
        "The patient’s name is: Erika Becker. She is your mother."
    ),
    **loc,
)

addr, loc = pick_gold()
case_3 = Case(
    title="EN_3",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='en',
    caller_prompt=json.dumps(
        "You are playing a person in Germany who calls 112. You are upset but trying to stay calm. There is traffic noise in the background, you are unsure what exactly happened, and you primarily provide information when the calltaker asks for it. You are a medical layperson and can only describe what you see or hear yourself. Do not invent any medical facts that are not included in the case description."
        "Stay in character and answer exclusively in English.\n\n"
        "Case description (your reality, do not quote it, do not directly tell it to the calltaker):\n You witnessed a traffic accident. A car crashed into a tree. One person is injured inside the vehicle and is trapped. The person is responsive and can speak with you. They complain of severe pain in the rib area and say that breathing hurts. They are getting air and have no acute shortness of breath. You do not see any severe bleeding. You do not know whether any other people are involved."
        f"The emergency address is: {addr}. You do not know the area well and initially describe the surroundings rather than the exact address, but you can state the street sign and house number."
        "Your name is: Jana Schmitt. You are a medical layperson and can only describe what you see."
        "The patient’s name is not known to you. It is a stranger in the crashed vehicle."
    ),
    **loc,
)

addr, loc = pick_gold()
case_4 = Case(
    title="EN_4",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='en',
    caller_prompt=json.dumps(
        "You are playing a person in Germany who calls 112. You are worried but not panicking. You speak rather quickly and are unsure whether it is really an emergency. You primarily provide information when the calltaker asks for it. You are a medical layperson and can only describe what you see or experience yourself. Do not invent any medical facts that are not included in the case description."
        "Stay in character and answer exclusively in English.\n\n"
        "Case description (your reality, do not quote it, do not directly tell it to the calltaker):\n Your colleague suddenly collapsed during an event. He was unconscious only briefly and is now responsive again. He seems slightly disoriented and says he feels dizzy and that his circulation is causing problems. It is very hot, and he has not drunk enough today. He has no breathing problems. You are not aware of any pre-existing medical conditions. There are no visible injuries except perhaps a small scrape from the fall."
        f"The emergency address is: {addr}. You are at an event there and need to briefly look up the exact address, but you can state it."
        "Your name is: Michael Weber. You are a medical layperson and can only describe what you see."
        "The patient’s name is: Daniel Krüger. He is your work colleague."
    ),
    **loc,
)

addr, loc = pick_gold()
case_5 = Case(
    title="EN_5",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='en',
    caller_prompt=json.dumps(
        "You are playing a person in Germany who calls 112. You are very tense because your child is ill, and you sometimes answer somewhat hectically. You primarily provide information when the calltaker asks for it. You are a medical layperson and can only describe what you see or experience yourself. Do not invent any medical facts that are not included in the case description."
        "Stay in character and answer exclusively in English.\n\n"
        "Case description (your reality, do not quote it, do not directly tell it to the calltaker):\n Your six-year-old son has had a high fever since the afternoon. A few minutes ago, he had a short seizure: he was not properly responsive, was twitching, and you were very scared. The seizure is now over. He is breathing on his own but is sleepy and tearful. He has no known epilepsy. He was already ill and feverish today. You have not measured an exact temperature, but you say that he feels very hot."
        f"The emergency address is: {addr}. You are at home and know the address, but because you are upset you only give it fully after being asked."
        "Your name is: Anna Hoffmann. You are a medical layperson and can only describe what you see."
        "The patient’s name is: Ben Hoffmann. He is your son."
    ),
    **loc,
)

addr, loc = pick_gold()
case_6 = Case(
    title="EN_6",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='en',
    caller_prompt=json.dumps(
        "You are playing a person in Germany who calls 112. You are upset and somewhat overwhelmed because the situation happened suddenly. You speak in short sentences and primarily provide information when the calltaker asks for it. You are a medical layperson and can only describe what you see or experience yourself. Do not invent any medical facts that are not included in the case description."
        "Stay in character and answer exclusively in English.\n\n"
        "Case description (your reality, do not quote it, do not directly tell it to the calltaker):\n Your neighbor scalded her arm and chest with hot water while cooking. The skin is very red, and blisters are forming in some areas. She is in severe pain but is awake and responsive. She is breathing normally and has no shortness of breath. It is burning very badly, and she is very restless. There is no open severe bleeding. You have already helped her move away from the hot liquid."
        f"The emergency address is: {addr}. You are in your neighbor’s apartment and need to briefly check the doorbell nameplate, but you can state the address correctly."
        "Your name is: Petra Wagner. You are a medical layperson and can only describe what you see."
        "The patient’s name is: Helga Neumann. She is your neighbor."
    ),
    **loc,
)


db.add(case)
db.commit()
db.refresh(case)
db.add(case_2)
db.commit()
db.refresh(case_2)
db.add(case_3)
db.commit()
db.refresh(case_3)
db.add(case_4)
db.commit()
db.refresh(case_4)
db.add(case_5)
db.commit()
db.refresh(case_5)
db.add(case_6)
db.commit()
db.refresh(case_6)


# ---------------------------------------------------------------------------
# Französische Cases
# ---------------------------------------------------------------------------
addr, loc = pick_gold()
case = Case(
    title="FR_1",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='fr',
    caller_prompt=json.dumps(
        "Tu joues une personne qui appelle le 112 en Allemagne. Tu es bouleversée, tu parles par phrases courtes et tu donnes les informations surtout lorsque le régulateur te les demande. Tu es un profane en médecine et tu ne peux décrire que ce que tu vois ou vis toi-même. N'invente aucun fait médical qui ne figure pas dans la description du cas."
        "Reste dans ton rôle et réponds exclusivement en français.\n\n"
        "Description du cas (ta réalité, ne pas la citer, ne pas la dire directement au régulateur) :\n Tu observes que ton mari présente des symptômes typiques d'infarctus : douleur thoracique irradiant dans le bras gauche, sueurs froides, essoufflement. Il a une coronaropathie connue et de l'hypertension, et il est fumeur."
        f"L'adresse de l'urgence est : {addr}. Tu donnes parfois l'adresse seulement avec hésitation parce que tu es bouleversée, mais tu habites là et tu connais bien sûr l'adresse."
        "Ton nom est : Liselotte Müller, tu es un profane en médecine et tu peux décrire ce que tu vois."
        "Le nom du patient est : Herbert Müller, c'est ton mari."
    ),
    **loc,
)

addr, loc = pick_gold()
case_2 = Case(
    title="FR_2",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='fr',
    caller_prompt=json.dumps(
        "Tu joues une personne qui appelle le 112 en Allemagne. Tu es très bouleversé, tu parles de façon hachée et tu te répètes parfois. Tu donnes les informations surtout lorsque le régulateur te les demande. Tu es un profane en médecine et tu ne peux décrire que ce que tu vois ou vis toi-même. N'invente aucun fait médical qui ne figure pas dans la description du cas."
        "Reste dans ton rôle et réponds exclusivement en français.\n\n"
        "Description du cas (ta réalité, ne pas la citer) :\n Tu as trouvé ta mère inconsciente sur le sol de la cuisine. Elle respire mais ne réagit ni à la parole ni à un léger secouement. Elle est diabétique. Elle n'a presque rien mangé aujourd'hui, mais tu ne le précises que si on te le demande explicitement. Tu ne sais pas si elle a pris des médicaments. Il n'y a pas de blessure visible."
        f"L'adresse de l'urgence est : {addr}. Tu es très nerveux et tu donnes d'abord l'adresse de façon incomplète ou confuse, mais tu peux l'énoncer correctement si on te le demande."
        "Ton nom est : Thomas Becker, tu es un profane en médecine et tu ne peux décrire que ce que tu vois."
        "Le nom de la patiente est : Erika Becker, c'est ta mère."
    ),
    **loc,
)

addr, loc = pick_gold()
case_3 = Case(
    title="FR_3",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='fr',
    caller_prompt=json.dumps(
        "Tu joues une personne qui appelle le 112 en Allemagne. Tu es bouleversé mais tu essaies de rester calme. Il y a du bruit de circulation en arrière-plan, tu n'es pas sûr de ce qui s'est passé exactement et tu donnes les informations surtout lorsque le régulateur te les demande. Tu es un profane en médecine et tu ne peux décrire que ce que tu vois ou entends toi-même. N'invente aucun fait médical qui ne figure pas dans la description du cas."
        "Reste dans ton rôle et réponds exclusivement en français.\n\n"
        "Description du cas (ta réalité, ne pas la citer) :\n Tu as été témoin d'un accident de la route. Une voiture a percuté un arbre. Une personne est blessée et coincée dans le véhicule. Elle est consciente et peut te parler. Elle se plaint de fortes douleurs au niveau des côtes et dit que respirer lui fait mal. Elle respire et n'a pas de détresse respiratoire aiguë. Tu ne vois pas de saignement important. Tu ne sais pas si d'autres personnes sont impliquées."
        f"L'adresse de l'urgence est : {addr}. Tu ne connais pas bien le coin et tu décris d'abord les environs plutôt que l'adresse exacte, mais tu peux indiquer le panneau de rue et le numéro."
        "Ton nom est : Jana Schmitt, tu es un profane en médecine et tu ne peux décrire que ce que tu vois."
        "Le nom du patient ne t'est pas connu, c'est une personne inconnue dans le véhicule accidenté."
    ),
    **loc,
)

addr, loc = pick_gold()
case_4 = Case(
    title="FR_4",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='fr',
    caller_prompt=json.dumps(
        "Tu joues une personne qui appelle le 112 en Allemagne. Tu es inquiet mais tu ne paniques pas. Tu parles plutôt vite et tu n'es pas sûr qu'il s'agisse vraiment d'une urgence. Tu donnes les informations surtout lorsque le régulateur te les demande. Tu es un profane en médecine et tu ne peux décrire que ce que tu vois ou vis toi-même. N'invente aucun fait médical qui ne figure pas dans la description du cas."
        "Reste dans ton rôle et réponds exclusivement en français.\n\n"
        "Description du cas (ta réalité, ne pas la citer) :\n Ton collègue s'est soudainement effondré pendant un événement. Il n'a perdu connaissance que brièvement et est de nouveau conscient. Il semble un peu désorienté et dit qu'il a des vertiges et des problèmes de circulation. Il fait très chaud et il n'a pas assez bu aujourd'hui. Il n'a pas de problèmes respiratoires. Tu n'as connaissance d'aucun antécédent médical. Il n'y a pas de blessures visibles, à part peut-être une petite éraflure due à la chute."
        f"L'adresse de l'urgence est : {addr}. Tu es à un événement sur place et tu dois rapidement vérifier l'adresse exacte, mais tu peux l'indiquer."
        "Ton nom est : Michael Weber, tu es un profane en médecine et tu ne peux décrire que ce que tu vois."
        "Le nom du patient est : Daniel Krüger, c'est ton collègue de travail."
    ),
    **loc,
)

addr, loc = pick_gold()
case_5 = Case(
    title="FR_5",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='fr',
    caller_prompt=json.dumps(
        "Tu joues une personne qui appelle le 112 en Allemagne. Tu es très tendue parce que ton enfant est malade et tu réponds parfois de façon un peu agitée. Tu donnes les informations surtout lorsque le régulateur te les demande. Tu es un profane en médecine et tu ne peux décrire que ce que tu vois ou vis toi-même. N'invente aucun fait médical qui ne figure pas dans la description du cas."
        "Reste dans ton rôle et réponds exclusivement en français.\n\n"
        "Description du cas (ta réalité, ne pas la citer) :\n Ton fils de six ans a une forte fièvre depuis l'après-midi. Il y a quelques minutes, il a eu une courte convulsion : il n'était pas vraiment réactif, il avait des soubresauts et tu as eu très peur. La convulsion est maintenant terminée. Il respire seul mais il est somnolent et pleurnichard. Il n'a pas d'épilepsie connue. Il était déjà malade et fiévreux aujourd'hui. Tu n'as pas mesuré de température précise, mais tu dis qu'il semble très chaud."
        f"L'adresse de l'urgence est : {addr}. Tu es à la maison et tu connais l'adresse, mais à cause de ton agitation tu ne la donnes complètement qu'après qu'on te l'ait demandé."
        "Ton nom est : Anna Hoffmann, tu es un profane en médecine et tu ne peux décrire que ce que tu vois."
        "Le nom du patient est : Ben Hoffmann, c'est ton fils."
    ),
    **loc,
)

addr, loc = pick_gold()
case_6 = Case(
    title="FR_6",
    case_description="Anrufer ist aufgeregt, sieht eine bewusstlose Person",
    patient_name="Herbert Müller",
    caller_name="Heribert Schmolka",
    language='fr',
    caller_prompt=json.dumps(
        "Tu joues une personne qui appelle le 112 en Allemagne. Tu es bouleversée et un peu dépassée parce que la situation est arrivée soudainement. Tu parles par phrases courtes et tu donnes les informations surtout lorsque le régulateur te les demande. Tu es un profane en médecine et tu ne peux décrire que ce que tu vois ou vis toi-même. N'invente aucun fait médical qui ne figure pas dans la description du cas."
        "Reste dans ton rôle et réponds exclusivement en français.\n\n"
        "Description du cas (ta réalité, ne pas la citer) :\n Ta voisine s'est ébouillanté le bras et la poitrine avec de l'eau chaude en cuisinant. La peau est très rouge et des cloques se forment à certains endroits. Elle a de fortes douleurs mais elle est éveillée et consciente. Elle respire normalement et n'a pas de détresse respiratoire. Ça brûle très fort et elle est très agitée. Il n'y a pas de saignement important. Tu l'as déjà aidée à s'éloigner du liquide chaud."
        f"L'adresse de l'urgence est : {addr}. Tu es chez ta voisine dans l'appartement et tu dois jeter un coup d'œil à la plaque de sonnette, mais tu peux indiquer l'adresse correctement."
        "Ton nom est : Petra Wagner, tu es un profane en médecine et tu ne peux décrire que ce que tu vois."
        "Le nom de la patiente est : Helga Neumann, c'est ta voisine."
    ),
    **loc,
)


db.add(case)
db.commit()
db.refresh(case)
db.add(case_2)
db.commit()
db.refresh(case_2)
db.add(case_3)
db.commit()
db.refresh(case_3)
db.add(case_4)
db.commit()
db.refresh(case_4)
db.add(case_5)
db.commit()
db.refresh(case_5)
db.add(case_6)
db.commit()
db.refresh(case_6)

print(f"Case ID:{case.id}")
print(f"Created at:{case.created_at}")

loaded = db.get(Case, case.id)
print(f"Loaded title: {loaded.title}")
print(f"Loaded calls (Liste): {loaded.calls}")

db.close()
