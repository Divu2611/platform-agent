# Importing libraries.
import numpy as np

from tools.embeddings import open_ai_embeddings

from models import Embedding


# Updating the document - replacing '{' with '{{'.
def __update_document(data):
    data = str(data)
    data = data.replace("{", "{{").replace("}", "}}")

    return data


# Generating embeddings for the text chunks.
def __generate_embeddings(text_chunks, model, chunk_size, overlap):
    # text_chunks = __split_text(text, chunk_size, overlap)
    embeddings = []

    for chunk in text_chunks:
        response = open_ai_embeddings(chunk, model)
        embeddings.append(response.data[0].embedding)

    return embeddings


# Getting the relevant knowledge from the embeddings.
def get_relevant_knowledge(text, model="text-embedding-ada-002", limit=5, similarity_threshold=0.8, chunk_size=500, overlap=50):
    # Generate query embedding
    if len(text) > 1:
        text = [[item for subtext in text for item in subtext]]

    query_embedding = __generate_embeddings(text, model, chunk_size, overlap)
    query_embedding = np.array(query_embedding).flatten()

    # Fetch relevant embeddings using ORM
    embeddings = Embedding.objects.only(
                    ["url", "chunk", "embedding"]
                ).all()
    # Compute cosine similarity manually
    relevant_embeddings = []
    for embedding in embeddings:
        stored_embedding = np.array(embedding.embedding, dtype=np.float32)  # Ensure stored embeddings are in a numerical format
        if(len(stored_embedding) == 0):
            continue

        cosine_similarity = np.dot(query_embedding, stored_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding))

        if cosine_similarity >= similarity_threshold:
            relevant_embeddings.append((cosine_similarity, embedding.chunk))

    # Sort by similarity score (highest first) and limit results
    relevant_embeddings.sort(reverse=True, key=lambda x: x[0])
    relevant_knowledge = [__update_document(item[1]) for item in relevant_embeddings[:limit]]

    return relevant_knowledge