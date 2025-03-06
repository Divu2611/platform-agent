# Importing Libraries.
import os
import json
from pydantic import SecretStr
# Importing LangChain Libraries.
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

from tools.key import tavily_api_key

# Construct the absolute path to the config.json file.
__config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/config.json"))
# Load JSON data
with open(__config_path, "r") as file:
    config = json.load(file)

# Initializing the Tavily Tool.
__tool = config["Tools"]["search"]["tavily"]

# Defining the Tavily Search Results.
tavily_search_tool = TavilySearchResults(
                        max_results = __tool["max_results"],
                        api_wrapper=TavilySearchAPIWrapper(tavily_api_key=SecretStr(tavily_api_key))
                    )