"""Populate the DB with example cases for the prototype."""
from app.database import Base, SessionLocal, engine
from app.models import ABCDEAssessment, Case, InjuryAssessment
from app.models.enums import CategoryEnum, SeverityEnum, SourceEnum


def seed() -> None:
    """Insert example cases and their truth assessments (idempotent)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Case).first():
            print("DB already has cases — skipping seed.")
            return

        case = Case(
            title="Herzinfarkt, 62-jähriger Mann",
            case_description=(
                "Du bist die Ehefrau eines 62-jährigen Mannes. Dein Mann hat seit "
                "20 Minuten starke Brustschmerzen, ist blass und schwitzt. Er ist "
                "ansprechbar, sitzt auf dem Sofa. Ihr seid zuhause in Berlin-Mitte. "
                "Du bist sehr aufgeregt und redest schnell."
            ),
            address="Unter den Linden 12, 10117 Berlin",
            gps_lat=52.5170,
            gps_lng=13.3889,
            patient_name="Klaus Müller",
            caller_name="Anna Müller",
        )
        db.add(case)
        db.flush()  # case.id needs to exist for the assessments below

        truths = [
            (CategoryEnum.A, SeverityEnum.NONE, ["Atemwege frei"]),
            (CategoryEnum.B, SeverityEnum.MILD, ["leichte Dyspnoe"]),
            (CategoryEnum.C, SeverityEnum.CRITICAL,
             ["starker retrosternaler Brustschmerz", "blass", "schwitzend"]),
            (CategoryEnum.D, SeverityEnum.NONE, ["GCS 15, orientiert"]),
            (CategoryEnum.E, SeverityEnum.NONE, []),
        ]
        for category, severity, findings in truths:
            db.add(ABCDEAssessment(
                case_id=case.id,
                source=SourceEnum.CASE_TRUTH,
                category=category,
                findings=findings,
                severity=severity,
            ))

        db.add(InjuryAssessment(
            case_id=case.id,
            source=SourceEnum.CASE_TRUTH,
            injuries=[],
        ))

        db.commit()
        print(f"Seeded case #{case.id}: {case.title}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()