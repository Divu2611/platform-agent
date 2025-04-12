# Importing Libraries.
import os
import json
import uuid
from pydantic import BaseModel, Field
# Importing LangChain Libraries.
from langchain_core.prompts import ChatPromptTemplate

from tools.database import create
from tools.llm import open_ai_chat_model

from utils.langsmith import langsmith_integration
from utils.prompt import get_system_prompt

# Construct the absolute path to the config.json file.
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.json"))
# Load JSON data
with open(config_path, "r") as file:
    config = json.load(file)


# LangSmith Integration.
langsmith_integration()



class GenerateQuestion(BaseModel):
    """Generate a question from the current understanding"""
    question: str | None = Field(default=None, description="Question from the current understanding")

class QuestionAgent:
    """Agent responsible in generating questions"""

    def __init__(self, client_id):
        # Initialize the Agent.
        __agent = config["Agents"]["question"]


        # Getting the system prompt.
        __system_prompt = get_system_prompt(agent_name = __agent["Name"], client_id = client_id)

        self.question_prompt = ChatPromptTemplate.from_messages([
                                    ("system", __system_prompt),
                                    ("human", "{understanding}"),
                                    ("human", "{question}")
                                ])


        # Getting the LLM Model.
        __llm = __agent["LLM"]
        __model = __agent["LLM Model"]
        __temperature = __agent["Temperature"]

        __llm_chat_model = f"{__llm}_chat_model"
        __llm_model = globals()[__llm_chat_model](model=__model, temperature=__temperature)

        self.chat_model = __llm_model.with_structured_output(GenerateQuestion)


        # Defining the question agent.
        run_id = str(uuid.uuid4())
        self.__trace(client_id = client_id, run_id = run_id, agent_id = __agent["ID"])
        # Creating the chain.
        self.chain = (self.question_prompt | self.chat_model).with_config({"run_id": run_id})


    def generate_question(self, question, current_understanding) -> GenerateQuestion:
        return self.chain.invoke(
            input={
                "understanding": current_understanding,
                "question": question
            }
        )


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