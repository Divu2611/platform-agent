from tools.database import SessionLocal, and_

from models import Agent

# Updating the document - replacing '{' with '{{'.
def __update_document(data):
    data = str(data)
    data = data.replace("{", "{{").replace("}", "}}")

    return data


# Getting the system prompt from the database.
def get_system_prompt(agent_name, platform_id):
    session = SessionLocal()

    agent_details = session.query(
                        Agent
                    ).filter(
                        and_(
                            Agent.agent_name == agent_name,
                            Agent.platform_id == platform_id
                        )
                    ).first()

    if agent_details:
        system_prompt = agent_details.system_prompt
        system_prompt = __update_document(system_prompt)

        session.close()

        return system_prompt