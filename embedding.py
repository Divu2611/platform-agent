from tools.embeddings import open_ai_embeddings


def chunk_text(text, delimiter, chunk_size):
        sentences = text.split(delimiter)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())

            if current_length + sentence_length > chunk_size:
                chunks.append(delimiter.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(delimiter.join(current_chunk))

        return chunks


def get_openai_embeddings(texts, model="text-embedding-ada-002", delimiter='.', chunk_size=100):
    all_embeddings = []
    chunks = []

    for text in texts:
        chunks = chunk_text(text, delimiter, chunk_size)

        for chunk in chunks:
            try:
                response = open_ai_embeddings([chunk], model)
                embeddings = response.data[0].embedding
                all_embeddings.append(embeddings)
            except Exception as e:
                print(f"Error generating embeddings for chunk: {e}")
                all_embeddings.append([])

    return all_embeddings, chunks