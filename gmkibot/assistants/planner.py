import autogen
import sys
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from gmkibot.utils import DBManager

def get_planning_agent (llm_config):
    planner = autogen.AssistantAgent(
        name="Planner",
        system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
        The plan may involve an engineer who can write code and a scientist who doesn't write code.
        Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
        """,
        llm_config=llm_config,
    )
    return planner

