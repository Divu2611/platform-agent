# Importing libraries.
import os
import json

from .connect import cluster

# Construct the absolute path to the config.json file.
__config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.json"))
# Load JSON data
with open(__config_path, "r") as file:
    config = json.load(file)


def create(keyspace, insert_query: str):
    # Get the timeout.
    timeout = config["Database"]["cassandra"]["insert_timeout"]

    session = cluster.connect()

    session.set_keyspace(keyspace)
    session.execute(insert_query, timeout = timeout)