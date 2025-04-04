from tools.database import SessionLocal

from models import Resource


# Getting the resource_id of the resources used by the agent, from the database.
def get_resource(agent_id):
    session = SessionLocal()

    resources = session.query(Resource).filter(Resource.agent_id == agent_id).all()
    if resources:
        resource_ids = [resource.id for resource in resources]

        session.close()

        return resource_ids