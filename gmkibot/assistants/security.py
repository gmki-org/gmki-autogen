import autogen
import sys
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from gmkibot.utils import DBManager

def send_verification_email (email):
    print ("Sending verification email to: ", email)

def check_if_member_exists (email):
    print ("Checking if member exists: ", email)
    return False

def get_security_agent (llm_config):
    security_agent = AssistantAgent (
        name = "security_agent",
        human_input_mode = "NEVER",
        llm_config = llm_config,
        code_execution_config = False,
        description = "Manages security of the system. Can verify the membership status of a user based on his/her email address.",
        function_map = {
            # "send_verification_email": send_verification_email,
            "check_if_member_exists": check_if_member_exists,
        },
        system_message = """
        Du bist ein freundlicher aber sehr misstrauischer Sicherheitsagent. Du bist verantwortlich für die Sicherheit des Systems und musst sicherstellen, dass nur autorisierte Benutzer auf das System zugreifen können. Du kannst die Mitgliedschaft eines Benutzers überprüfen und Benutzer über eine 2-Faktor-Authentifizierung authentifizieren. Hierfür benötigste du die E-Mail-Adresse des Benutzers. 
        """ 
    )
    return security_agent    


