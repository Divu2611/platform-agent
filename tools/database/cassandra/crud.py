from .connect import cluster


def create(keyspace, insert_query: str):
    session = cluster.connect()

    session.set_keyspace(keyspace)
    session.execute(insert_query)