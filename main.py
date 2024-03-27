import autogen
import sys
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from gmkibot.utils import DBManager
from gmkibot.assistants import security, planner

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
print(config_list)

llm_config_agents = {
    "functions": [
        {
            "name": "check_if_member_exists",
            "description": "Use the email address to check if a member exists in the database. Return True if the member exists, False otherwise.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The email address of the member.",
                    },
                },
                "required": ["email"],
            },
        },
    ],
    "config_list": config_list,
    "timeout": 120,
}

llm_config_groupchat = {
    "config_list": config_list,
    "timeout": 120,
}

user_proxy_prompt = """
Du bist ein freundlicher und hilfsbereiter Admin und versuchst dem User zu helfen. Um den User zu unterstützen, kannst du den Sicherheitsagenten und den Planungsagenten um Hilfe bitten. Bevor Du auf Fragen des Users antwortest, überprüfe bitte, ob der User ein bekanntes Mitglied ist. Hierfür benötigst du die E-Mail-Adresse des Users. Erst wenn Du diese hast, kannst Du dem User helfen. 
"""

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "workdir",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    human_input_mode="ALWAYS",
)

security_agent = security.get_security_agent(llm_config_agents)
planner = planner.get_planning_agent(llm_config_agents)

groupchat = autogen.GroupChat(agents=[user_proxy, security_agent, planner], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_groupchat)

user_proxy.initiate_chat(
    manager, message="Finde als erstes heraus ob der User ein bekanntes Mitglied ist. Frage danach Du dem User helfen kannst."
)
# type exit to terminate the chat
sys.exit()

