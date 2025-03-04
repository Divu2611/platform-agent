# Importing Libraries.
import os
# Importing Cassandra Libraries.
from cassandra.cluster import Cluster

# Loading the environment variables.
from config import load_env_vars
load_env_vars()

# Connect to Cassandra
cluster = Cluster([os.getenv("cassandra_host")])  # Cassandra host