# Location-System Ausbau – steps.md (reorganisiert)

Reihenfolge nach Abhängigkeiten sortiert. Teil A = Korrekturen am bereits Umgesetzten, Teil B = verbleibende Schritte in ausführbarer Reihenfolge.

---

## Status

| Bereich | Status |
|---|---|
| Enums (`ADDRESS_AGENT`, `ON_SCENE_AGENT`, `AMLAccuracyEnum`) | ✅ korrekt |
| `app/models/address_db.py` (AddressDB) | ✅ korrekt |
| `app/models/case.py` (FK + aml-Felder + Relationship) | ✅ korrekt |
| `app/schemas/case.py` | ⚠️ 2 Fehler (siehe A1, A2) |
| `import_addresses.py` | ⚠️ doppelter Import (A3) |

---

# Teil A – Korrekturen am bereits Umgesetzten

## A1: `CaseRead` crasht (PFLICHT)

**Datei:** `app/schemas/case.py`

**Problem:** `gps_lat` / `gps_lng` existieren nicht mehr im Case-Modell. `from_attributes=True` lässt Pydantic `case.gps_lat` lesen → Fehler bei jedem `GET /cases`.

**Fix:**
```python
from app.models.enums import LanguageEnum, AMLAccuracyEnum

class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    language: LanguageEnum
    gold_address_id: int
    aml_lat: float | None
    aml_lon: float | None
    aml_accuracy: AMLAccuracyEnum | None
    patient_name: str
    caller_name: str
    created_at: datetime
```

## A2: `CaseCreate.gold_address_id` entfernen

**Problem:** Cases bekommen ihre Adresse automatisch (zufällig aus DB) beim Erstellen. Der Client kann die ID gar nicht kennen → Feld muss raus.

**Fix:**
```python
class CaseCreate(BaseModel):
    title: str
    case_description: str
    patient_name: str
    caller_name: str
    caller_prompt: str
    language: LanguageEnum = LanguageEnum.DE
    # gold_address_id NICHT hier – wird im Router gesetzt (siehe B5)
```

## A3: Doppelter Import in `import_addresses.py`

Zeile 2 löschen, Zeile 3 reicht:
```python
from app.database import Base, SessionLocal, engine   # diese behalten
```

---

# Wichtiger Hinweis: zwei `SourceEnum`

Es gibt **zwei gleichnamige** Enums – beim Importieren genau hinschauen:

| Import | Werte | Wofür |
|---|---|---|
| `from app.models.enums import SourceEnum` | `CASE_TRUTH, CALL_TAKER, AI_AGENT` | Assessment-Herkunft (B2, B4) |
| `from app.models.address import SourceEnum` | `TRANSCRIPT, ADDRESS_DATABASE, ...` | Address-Objekt-Herkunft |

Für `AddressAssessment` / `OnSceneAssessment` nutzen wir **`app.models.enums.SourceEnum.AI_AGENT`**.

---

# Teil B – Verbleibende Schritte (in dieser Reihenfolge)

Reihenfolge wichtig: **B1 (matching.py) muss vor B5 (Router)** existieren, weil der Router `simulate_aml` daraus importiert.

---

## B1: Matching-Logik + AML-Helfer

**Neue Dateien:**
- `app/simulation/location/__init__.py` (leer)
- `app/simulation/location/matching.py`

**Warum zuerst:** Diese Funktionen sind die Grundlage. Sie sind kein „Agent“ – sie werden vom Router (B5) und von den Agenten (B3) aufgerufen. Reine Logik, keine Abhängigkeit zu Agenten/DB-Modellen außer `AddressDB`.

**Abhängigkeit:** `rapidfuzz` in `requirements.txt` ergänzen + `pip install rapidfuzz`.

**Inhalt `matching.py`:**
```python
import re, math, random
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from app.models.address_db import AddressDB
from app.models.enums import AMLAccuracyEnum


def normalize_text(s: str) -> str:
    """Lowercase, Umlaute auflösen, Satzzeichen entfernen – für Fuzzy-Matching."""
    if not s:
        return ""
    s = s.lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[^\w\s]", "", s)
    return s.strip()


def normalize_hn(hn: str) -> str:
    """Hausnummern: Uppercase, keine Leerzeichen."""
    if not hn:
        return ""
    return re.sub(r"\s+", "", hn.upper())


def fuzzy_best(value: str, candidates: list[str], min_score: int = 70) -> tuple[str | None, int]:
    """Bester Fuzzy-Match für value in candidates (token_sort_ratio)."""
    best_match, best_score = None, 0
    for candidate in candidates:
        score = fuzz.token_sort_ratio(value, candidate)
        if score > best_score:
            best_score, best_match = score, candidate
    return (best_match, best_score) if best_score >= min_score else (None, best_score)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """GPS-Distanz zweier Punkte in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_addresses_within_radius(lat: float, lon: float, radius_km: float, db: Session) -> list[AddressDB]:
    """DB-Adressen im GPS-Radius. Erst grobe Box (schnell), dann exakte Distanz."""
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * math.cos(math.radians(lat)))
    candidates = db.query(AddressDB).filter(
        AddressDB.lat.between(lat - delta_lat, lat + delta_lat),
        AddressDB.lon.between(lon - delta_lon, lon + delta_lon),
    ).all()
    return [a for a in candidates if haversine_km(lat, lon, a.lat, a.lon) <= radius_km]


def find_address_adaptive(city, street, housenumber, db: Session, min_score: int = 75) -> list[AddressDB]:
    """Mehrstufige Adresssuche gegen DB: Stadt → Straße → Hausnummer (Fuzzy)."""
    city_norm = normalize_text(city or "")
    street_norm = normalize_text(street or "")
    hn_norm = normalize_hn(housenumber or "")

    all_cities = [r[0] for r in db.query(AddressDB.city_norm).distinct().all()]
    best_city, _ = fuzzy_best(city_norm, all_cities, min_score)
    if not best_city:
        return []

    city_addrs = db.query(AddressDB).filter(AddressDB.city_norm == best_city).all()
    city_streets = list({a.street_norm for a in city_addrs})
    best_street, _ = fuzzy_best(street_norm, city_streets, min_score)
    if not best_street:
        return []

    street_addrs = [a for a in city_addrs if a.street_norm == best_street]
    if hn_norm:
        hn_candidates = [a.hn_norm for a in street_addrs if a.hn_norm]
        best_hn, _ = fuzzy_best(hn_norm, hn_candidates, 80)
        if best_hn:
            matched = [a for a in street_addrs if a.hn_norm == best_hn]
            if matched:
                return matched
    return street_addrs


def blur_gps(lat: float, lon: float, min_km: float, max_km: float) -> tuple[float, float]:
    """Verschiebt GPS um zufällige Distanz/Richtung (AML-Simulation)."""
    distance_km = random.uniform(min_km, max_km)
    angle = random.uniform(0, 2 * math.pi)
    delta_lat = (distance_km / 111.0) * math.cos(angle)
    delta_lon = (distance_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(angle)
    return lat + delta_lat, lon + delta_lon


def simulate_aml(lat: float, lon: float) -> tuple[float, float, AMLAccuracyEnum]:
    """Simuliert Handy-Ortung mit zufälliger Genauigkeit. Vom Router (B5) genutzt."""
    r = random.random()
    if r < 0.35:
        acc, (la, lo) = AMLAccuracyEnum.HIGH_ACCURACY, blur_gps(lat, lon, 0, 0.05)
    elif r < 0.70:
        acc, (la, lo) = AMLAccuracyEnum.MEDIUM_ACCURACY, blur_gps(lat, lon, 0, 0.15)
    elif r < 0.90:
        acc, (la, lo) = AMLAccuracyEnum.LOW_ACCURACY, blur_gps(lat, lon, 0, 0.5)
    else:
        acc, (la, lo) = AMLAccuracyEnum.VERY_LOW_ACCURACY, blur_gps(lat, lon, 0.5, 5.0)
    return la, lo, acc
```

---

## B2: Assessment-Modelle + Call-Relationships

**Dateien:** `app/models/assessment.py` (ergänzen), `app/models/call.py`, `app/models/__init__.py`

**Warum vor den Agenten:** Die Agenten (B3) schreiben in diese Tabellen – also müssen die Modelle vorher existieren.

In `app/models/assessment.py` ergänzen (Imports: `JSON`, `ForeignKey`, `SourceEnum` aus `app.models.enums`):
```python
class AddressAssessment(Base):
    __tablename__ = "address_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))
    agent_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    source: Mapped[SourceEnum] = mapped_column(SQLEnum(SourceEnum), default=SourceEnum.AI_AGENT)
    address_candidates: Mapped[list] = mapped_column(JSON, default=list)   # roher LLM-Output
    matched_addresses: Mapped[list] = mapped_column(JSON, default=list)    # nach DB-Match + Distanz
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    call: Mapped["Call"] = relationship(back_populates="address_assessments")
    agent_run: Mapped[Optional["AgentRun"]] = relationship()


class OnSceneAssessment(Base):
    __tablename__ = "onscene_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"))
    agent_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    source: Mapped[SourceEnum] = mapped_column(SQLEnum(SourceEnum), default=SourceEnum.AI_AGENT)
    findings: Mapped[list] = mapped_column(JSON, default=list)   # zitierte Belege
    onscene_status: Mapped[str] = mapped_column(String(20))      # yes | no | unknown
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    call: Mapped["Call"] = relationship(back_populates="onscene_assessments")
    agent_run: Mapped[Optional["AgentRun"]] = relationship()
```

In `app/models/call.py` die Gegenseite der Relationship ergänzen:
```python
address_assessments: Mapped[list["AddressAssessment"]] = relationship(back_populates="call")
onscene_assessments: Mapped[list["OnSceneAssessment"]] = relationship(back_populates="call")
```

In `app/models/__init__.py` beide Klassen importieren + in `__all__` eintragen.

> ⚠️ **PFLICHT, leicht übersehen:** `app/main.py` ruft `Base.metadata.create_all()` und importiert `app.models`. Die Tabellen `address_assessments` / `onscene_assessments` entstehen **nur**, wenn die Klassen hier in `__init__.py` registriert sind. Fehlt der Eintrag, läuft der Agent zwar, aber `persist()` crasht beim Speichern (Tabelle existiert nicht).

---

## B3: Die zwei Agenten

**Dateien:** `app/simulation/agents/address_agent.py`, `app/simulation/agents/on_scene_agent.py`

**Warum jetzt:** Braucht B1 (matching) + B2 (Modelle).

**Wie `BaseAgent` aufgebaut ist** (`app/simulation/agents/base.py`): `__init__(self, call, db)` setzt `self.call` und `self.db`. In `persist()` also immer **`self.call`** (der Call) und **`self.call.case`** (das Case mit `aml_lat`/`aml_lon`) nutzen – nicht `run.call`. `run` ist die frisch angelegte `AgentRun`-Zeile; `run.id` / `run.call_id` sind nach dem `flush()` verfügbar.

### `address_agent.py`
```python
from app.models import AgentRun
from app.models.enums import AgentTypeEnum, SourceEnum     # AI_AGENT-Variante!
from app.models.address import AddressResult
from app.models.assessment import AddressAssessment
from app.simulation.agents.base import BaseAgent
from app.simulation.location.matching import find_address_adaptive, haversine_km


class AddressAgent(BaseAgent[AddressResult]):
    agent_type = AgentTypeEnum.ADDRESS_AGENT
    output_schema = AddressResult

    def build_prompt(self) -> str:
        return (
            "Du bist ein Adress-Extraktions-Agent in einer Rettungsleitstelle.\n\n"
            "Lies das Notruf-Transkript und extrahiere ALLE genannten Adressen/Ortsangaben.\n"
            "Pro Adresse: city, street, housenumber, postcode, type "
            "('emergency_location_primary' für Einsatzort, "
            "'emergency_location_alternative' für Alternativen, "
            "'caller_location' für eigenen Standort), special_notes, confidence (0.0-1.0).\n"
            'Antworte mit JSON: {"addresses": [...]}. Keine Adresse → {"addresses": []}. '
            "Erfinde nichts."
        )

    def persist(self, output: AddressResult, run: AgentRun) -> None:
        candidates = [a.model_dump() for a in output.addresses]
        case = self.call.case   # self.call wird in BaseAgent.__init__ gesetzt – garantiert geladen
        matched = []
        for a in output.addresses:
            for db_addr in find_address_adaptive(a.city, a.street, a.housenumber, self.db):
                dist = None
                if case.aml_lat and case.aml_lon:
                    dist = haversine_km(case.aml_lat, case.aml_lon, db_addr.lat, db_addr.lon)
                matched.append({
                    "id": db_addr.id, "city": db_addr.city, "street": db_addr.street,
                    "housenumber": db_addr.housenumber, "postcode": db_addr.postcode,
                    "lat": db_addr.lat, "lon": db_addr.lon, "gps_distance_km": dist,
                    "candidate_type": a.type,
                })
        matched.sort(key=lambda x: (x["gps_distance_km"] is None, x.get("gps_distance_km") or 0))
        self.db.add(AddressAssessment(
            call_id=run.call_id, agent_run_id=run.id, source=SourceEnum.AI_AGENT,
            address_candidates=candidates, matched_addresses=matched,
        ))
```

### `on_scene_agent.py`
```python
from typing import Literal
from pydantic import BaseModel
from app.models import AgentRun
from app.models.enums import AgentTypeEnum, SourceEnum
from app.models.assessment import OnSceneAssessment
from app.simulation.agents.base import BaseAgent


class OnSceneAgentOutput(BaseModel):
    findings: list[str]
    onscene_status: Literal["yes", "no", "unknown"]
    confidence: float | None = None


class OnSceneAgent(BaseAgent[OnSceneAgentOutput]):
    agent_type = AgentTypeEnum.ON_SCENE_AGENT
    output_schema = OnSceneAgentOutput

    def build_prompt(self) -> str:
        return (
            "Bestimme, ob der Anrufer physisch am Einsatzort ist.\n"
            "'yes': 'ich bin bei', 'ich sehe', aktive Hilfe. "
            "'no': beschreibt Gefundenes aus der Ferne, anderer Ort. "
            "Unklar → 'unknown'.\n"
            'JSON: {"findings": ["zitat", ...], "onscene_status": "yes|no|unknown", "confidence": 0.0-1.0}'
        )

    def persist(self, output: OnSceneAgentOutput, run: AgentRun) -> None:
        self.db.add(OnSceneAssessment(
            call_id=run.call_id, agent_run_id=run.id, source=SourceEnum.AI_AGENT,
            findings=output.findings, onscene_status=output.onscene_status,
            confidence=output.confidence,
        ))
```

---

## B4: Agent-Registry

**Datei:** `app/simulation/agents/__init__.py`

Beide neuen Agenten in die Registry/Map eintragen (analog zu den bestehenden):
```python
from app.simulation.agents.address_agent import AddressAgent
from app.simulation.agents.on_scene_agent import OnSceneAgent
# in der Registry/dem Dict:
AgentTypeEnum.ADDRESS_AGENT: AddressAgent,
AgentTypeEnum.ON_SCENE_AGENT: OnSceneAgent,
```

---

## B5: Cases-Router – automatische Adresse + AML

**Datei:** `app/routers/cases.py`

**Hinweis (war früher „Schritt 6“ und falsch):** Die Funktionen `blur_gps` / `simulate_aml` gehören **NICHT** in den Router – die liegen in `matching.py` (B1). Der Router **importiert und nutzt** sie nur.

```python
from sqlalchemy import func
from app.models.address_db import AddressDB
from app.simulation.location.matching import simulate_aml

@router.post("/cases", response_model=CaseRead)
def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    gold = db.query(AddressDB).order_by(func.random()).first()
    if not gold:
        raise HTTPException(status_code=500, detail="Keine Adressen in DB – import_addresses.py laufen lassen")
    aml_lat, aml_lon, aml_acc = simulate_aml(gold.lat, gold.lon)
    new_case = Case(
        **case_data.model_dump(),
        gold_address_id=gold.id, aml_lat=aml_lat, aml_lon=aml_lon, aml_accuracy=aml_acc,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case
```

`func.random()` = SQL `RANDOM()`, wählt direkt in SQLite eine Zufallszeile (lädt nicht alle Adressen nach Python).

---

## B6: Assessment-Schemas + `CallDetailRead`

**Dateien:** `app/schemas/assessment.py`, `app/schemas/call.py`

In `assessment.py`:
```python
class AddressAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; call_id: int; agent_run_id: int | None
    source: SourceEnum
    address_candidates: list[dict]
    matched_addresses: list[dict]
    created_at: datetime

class OnSceneAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; call_id: int; agent_run_id: int | None
    source: SourceEnum
    findings: list[str]
    onscene_status: str
    confidence: float | None
    created_at: datetime
```

In `CallDetailRead` (`app/schemas/call.py`) ergänzen:
```python
address_assessments: list[AddressAssessmentRead] = []
onscene_assessments: list[OnSceneAssessmentRead] = []
```

---

## B7: `example_case.py` anpassen

Hardcodierte `address` / `gps_lat` / `gps_lng` aus den Case-Dicts entfernen. Vor dem Erstellen je Case eine Zufallsadresse holen + `simulate_aml` (analog B5), oder das Seed-Skript über `POST /cases` laufen lassen.

---

## B8: DB neu aufbauen + befüllen + testen

```bash
pip install rapidfuzz                 # falls noch nicht
# sim.db löschen (Schema hat sich geändert: Case-Felder getauscht)
rm sim.db
python import_addresses.py            # → "Import abgeschlossen: XXXXX Adressen in DB"
uvicorn app.main:app --reload
```

---

# Verifikation

1. `python import_addresses.py` → Count > 0
2. `POST /cases` → Response hat `gold_address_id`, `aml_lat/lon`, `aml_accuracy` (kein Crash → A1 ok)
3. `GET /cases/{id}` → kein 500er
4. Call anlegen, Nachrichten schreiben
5. `POST /calls/{id}/agents/address_agent` → AgentRun `success`, `AddressAssessment` mit `matched_addresses` (inkl. `gps_distance_km`) in DB
6. `POST /calls/{id}/agents/on_scene_agent` → `OnSceneAssessment` mit `yes/no/unknown`
7. `GET /calls/{id}` → enthält `address_assessments` + `onscene_assessments`

---

# Offen / später

- `location_agent.py` (alt) wird durch `address_agent` ersetzt → kann später raus
- Caller-Prompts in `example_case.py` enthalten hardcodierte Adressen → idealerweise dynamisch aus Gold-Adresse
- `get_addresses_radius()` aus dem Notebook → optionaler `AMLRadiusAgent` später
- `rapidfuzz` Version pinnen (z.B. `rapidfuzz>=3.0`)
