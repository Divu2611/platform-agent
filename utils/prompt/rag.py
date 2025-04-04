# Importing libraries.
import numpy as np

from tools.database import SessionLocal, and_
from tools.embeddings import open_ai_embeddings

from models import Embedding

# Updating the document - replacing '{' with '{{'.
def __update_document(data):
    data = str(data)
    data = data.replace("{", "{{").replace("}", "}}")

    return data


# Splitting the text into chunks.
def __split_text(text, chunk_size, overlap):
    chunks = []
    start = 0
    end = 0

    while end < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        chunks.append(text[start:end])
        start = end - overlap  # Overlap chunks

    return chunks


# Generating embeddings for the text chunks.
def __generate_embeddings(text_chunks, model, chunk_size, overlap):
    # text_chunks = __split_text(text, chunk_size, overlap)
    embeddings = []

    for chunk in text_chunks:
        response = open_ai_embeddings(chunk, model)
        embeddings.append(response.data[0].embedding)

    return embeddings


# Getting the relevant knowledge from the embeddings.
def get_relevant_knowledge(text, resource_ids, model = "text-embedding-ada-002", limit : int = 10, similarity_threshold : float = 0.6, chunk_size : int = 500, overlap : int = 50):
    session = SessionLocal()

    if len(text) > 1:
        text = [[item for subtext in text for item in subtext]]

    query_embedding = __generate_embeddings(text, model, chunk_size, overlap)
    query_embedding = np.array(query_embedding).flatten()

    embeddings = session.query(
                Embedding,
                Embedding.embedding.cosine_distance(query_embedding).label("distance")
            ).filter(
                and_(
                    Embedding.embedding.cosine_distance(query_embedding) < similarity_threshold,
                    Embedding.resource_id.in_(resource_ids)
                )
            ).order_by(
                "distance"
            ).limit(
                limit
            ).all()

    if embeddings:
        relevant_knowledge = [__update_document(embedding[0].chunk) for embedding in embeddings]

        session.close()

        return relevant_knowledge