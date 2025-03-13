from .connect import SessionLocal, text

def create(insert_query: str):
    session = SessionLocal()

    session.execute(text(insert_query))
    session.commit()

    session.close()


def retrieve(retrieve_query: str):
    session = SessionLocal()

    result = session.execute(text(retrieve_query))
    session.commit()

    rows = [list(row) for row in result.fetchall()]
    columns = list(result.keys())

    return rows, columns


def update(update_query: str):
    session = SessionLocal()

    session.execute(text(update_query))
    session.commit()

    session.close()


def delete(delete_query: str):
    session = SessionLocal()

    session.execute(text(delete_query))
    session.commit()

    session.close()