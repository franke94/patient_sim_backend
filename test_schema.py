from app.database import SessionLocal
from app.models import Case
from app.schemas import CaseRead

db = SessionLocal()
first_case = db.query(Case).first()

if first_case:
    pydantic_case = CaseRead.model_validate(first_case)
    print(pydantic_case.model_dump_json(indent=2))
else:
    print("Keine Case in der DB — lege eine an wie in Schritt 8c")

db.close()