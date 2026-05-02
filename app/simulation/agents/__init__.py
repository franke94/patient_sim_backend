from app.models.enums import AgentTypeEnum
from app.simulation.agents.a_agent import AAgent
from app.simulation.agents.location_agent import LocationAgent
from app.simulation.agents.single_agent import SingleAgent

from app.simulation.agents.abcde_agents import make_abcde_agent

AGENT_REGISTRY = {
    AgentTypeEnum.A_AGENT: make_abcde_agent(AgentTypeEnum.A_AGENT),
    AgentTypeEnum.B_AGENT: make_abcde_agent(AgentTypeEnum.B_AGENT),
    AgentTypeEnum.C_AGENT: make_abcde_agent(AgentTypeEnum.C_AGENT),
    AgentTypeEnum.D_AGENT: make_abcde_agent(AgentTypeEnum.D_AGENT),
    AgentTypeEnum.E_AGENT: make_abcde_agent(AgentTypeEnum.E_AGENT),
    AgentTypeEnum.LOCATION_AGENT: LocationAgent,
    AgentTypeEnum.SINGLE_AGENT: SingleAgent
}


"""
Andere version: Generisch für jeden Agent, das sollte aber noch ausgebaut werden!

AGENT_REGISTRY: dict[AgentTypeEnum, type] = {
    AgentTypeEnum.A_AGENT: AAgent,
    AgentTypeEnum.LOCATION_AGENT: LocationAgent,
    #B-E kommt später
}
"""
def get_agent_class(agent_type: AgentTypeEnum):
    if agent_type not in AGENT_REGISTRY:
        raise KeyError(f"No agent implemented for type '{agent_type.value}'")
    return AGENT_REGISTRY[agent_type]

__all__ = ["AGENT_REGISTRY", "get_agent_class"]