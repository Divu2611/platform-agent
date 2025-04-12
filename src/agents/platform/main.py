# Importing Libraries.
import os
import json
import uuid
from pydantic import BaseModel, Field
# Importing LangChain Libraries.
from langchain_core.prompts import ChatPromptTemplate

from tools.database import create
from tools.llm import open_ai_chat_model
from tools.web import tavily_search_tool

from utils.langsmith import langsmith_integration
from utils.prompt import get_system_prompt, get_relevant_knowledge
from utils import get_resource

# Construct the absolute path to the config.json file.
__config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.json"))
# Load JSON data
with open(__config_path, "r") as file:
    config = json.load(file)


# LangSmith Integration.
langsmith_integration()


class Acknowledge(BaseModel):
    """A acknowledgement answer to the user"""
    response: str = Field(
        description="Answer to acknowledge the user"
    )

class PlatformAgent:
    def __init__(self, client_id, question, messages):
        # Initialize the Agent.
        __agent = config["Agents"]["platform"]


        # Getting the system prompt.
        __system_prompt = get_system_prompt(agent_name = __agent["Name"], client_id = client_id)

        # Getting the relevant information via RAG.
        if not messages:
            messages = [question]
        # Getting the resource_ids used by the agent.
        agent_id = __agent["ID"]
        resource_ids = get_resource(agent_id)
        __relevant_information = get_relevant_knowledge(text = messages, resource_ids = resource_ids)

        self.platform_prompt = ChatPromptTemplate.from_messages([
                                        ("system", __system_prompt),
                                        ("system", __relevant_information),
                                        ("placeholder", "{question}")
                                    ])


        # Getting the tools.
        self.search_tool = tavily_search_tool


        # Getting the LLM Model.
        __llm = __agent["LLM"]
        __model = __agent["LLM Model"]
        __temperature = __agent["Temperature"]

        __llm_chat_model = f"{__llm}_chat_model"
        __llm_model = globals()[__llm_chat_model](model=__model, temperature=__temperature)

        self.chat_model = __llm_model.bind_tools([self.search_tool]).with_structured_output(Acknowledge)


        # Defining the platform agent.
        run_id = str(uuid.uuid4())
        self.__trace(client_id = client_id, run_id = run_id, agent_id = __agent["ID"])
        # Creating the chain.
        self.chain = (self.platform_prompt | self.chat_model).with_config({"run_id": run_id})


    def acknowledge(self, question) -> Acknowledge:
        response = self.chain.invoke({"question": [("user", question)]})
        return response.response


    def __trace(self, client_id: int, run_id: str, agent_id: int):
        """Trace the understanding agent"""

        try:
            # Create a new trace in the database
            insert_query = f'''
                INSERT INTO public.agent_run_history(client_id, run_id, agent_id)
                VALUES ({client_id}, '{run_id}', {agent_id})
            '''

            create(insert_query = insert_query)
        except Exception as exception:
            raise exception