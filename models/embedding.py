import uuid
# Importing Cassandra Libraries.
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.connection import setup
from cassandra.cqlengine.management import sync_table


# Setup ORM connection
setup(["127.0.0.1"], "irona")


class Embedding(Model):
    __keyspace__ = "irona"
    __table_name__ = "embeddings"

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    chunk = columns.Text()
    created_at = columns.DateTime()
    updated_at = columns.DateTime()
    url = columns.Text()
    embedding = columns.List(columns.Float)

# Sync model with the Cassandra table
sync_table(Embedding)