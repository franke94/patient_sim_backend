from app.models import AgentRun
from app.models.enums import AgentTypeEnum, SourceEnum     # AI_AGENT-Variante!
from app.models.address import AddressResult
from app.models.assessment import AddressAssessment
from app.simulation.agents.base import BaseAgent

from app.simulation.location.matching_rich import get_addresses_from_db


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
        case = self.call.case
        matched = get_addresses_from_db(output.addresses, case.aml_lat, case.aml_lon)
        self.db.add(AddressAssessment(
            call_id=run.call_id, agent_run_id=run.id, source=SourceEnum.AI_AGENT,
            address_candidates=[a.model_dump() for a in output.addresses],
            matched_addresses=[a.model_dump() for a in matched],  # enthält osm_id, lat/lon, confidence, fuzzy_mode
        ))